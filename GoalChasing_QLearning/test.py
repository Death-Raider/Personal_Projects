from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
from Agents.DQAgent import DQAgent
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import time
import logging

logging.basicConfig(filename='GoalChasing_QLearning/output.log', filemode='a', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('goal_chasing')


def create_random_agents(id,board_size)->list[Robot,Goal]:
    r1 = Robot(id = id)
    g1 = Goal(id = id)

    r1.set_random_init_state(board_size, board_size)
    r1.v = 1
    g1.set_random_goal(board_size, board_size)
    print(r1.get_dist(g1)[0])
    while r1.get_dist(g1)[0] < board_size*0.50:
        g1.set_random_goal(board_size, board_size)
    return [r1,g1]

def reset_positions(players, board_size):
    for i,[r,g,a] in enumerate(players):
        r.set_random_init_state(board_size, board_size)
        r.v = 1
        g.set_random_goal(board_size, board_size)
        # print(r.get_dist(g)[0])
        while r.get_dist(g)[0] < board_size*0.50:
            g.set_random_goal(board_size, board_size)

def calculate_reward(r: Robot, g: Goal, move_success):
    distance = r.get_dist(g)[0] # get_dist return [distance, angle(in radian)]
    angle_dir = r.DIR_ANGLES[r.dir]*np.pi/180

    angle_error = abs(r.get_dist(g)[1] - angle_dir) % (2*np.pi)
    
    # Primary reward components
    reward = 2 * (1/distance)  # Distance incentive
    reward += 4 if distance < 1.3 else 0  # Distance incentive
    reward += 1 * np.cos(angle_error)  # Direction alignment
    reward -= 0.3  # Step penalty
    
    # Collision/behavior penalties
    if not move_success:
        reward -= 2

    # ---------- collision avoidance policy ----------------- #
    for i,r_o in enumerate(r.detected_robots['robot']):
        if r.detected_robots['pos'][i][0] < r.closeness_threshold/2:
            reward -= 0.3
        ro_angle = r_o.DIR_ANGLES[r_o.dir]*np.pi/180
        angle_diff = np.abs(angle_dir - ro_angle) % (2*np.pi)
        reward += np.cos(angle_diff/2)**2

    # Best case reward value:
    # best case steps on average = 15
    # min number of iter penalty = -0.3*15 = -4.5    # step penalty 
    # always decreasing distance 2*(sum from n=2 to 15 of 1/n) = 4.63645798646    # distance incentive
    # always moving in correct direction = 1*15    # direction alignment
    # colloision avoidance: 
    #       1. No robot is too close = 15 * -0.3 * 2 = -9   # average 2 robots whicha are close
    #       2. detected robots are only moving in similar direction to self = 10 * 1 * 2*integral from 0 to 1 of cos^2(x/2) dx = 27.6220647721  # +/- 57 degree variation
    # total reward = 33.7585227586
    # average reward over the episode = 33.7585227586 / 15 = 2.25056818391

    return reward

def create_figure(robot_count):
    """
        create the template figure and returns the proper axis for all the robots and the board.
        first column and first two rows are for the board. Rest are for robots
        
        Returns figure, board axis, list of robot axis
    """

    total_boxes = robot_count + 2 # plus two for the main board rowspan
    row_count = int(np.ceil(np.sqrt(total_boxes)))
    col_count = row_count
    print("grid size = ",row_count,col_count)
    plt.ion()
    main_fig = plt.figure(figsize=(20,20))
    gs = gridspec.GridSpec(row_count,col_count)
    ax1 = main_fig.add_subplot(gs[:2,0]) # main images
    axs = []
    for i in range(row_count):
        for j in range(col_count):
            if (i in (0,1)) and (j == 0): # reserved for the board axis
                continue
            ax = main_fig.add_subplot(gs[i, j])
            axs.append(ax)
    return main_fig, ax1, axs

robot_count = 10
board_size = 20
threshold = 3
state_dim = (2*threshold+1) * (2*threshold+1) * 2 + 2 
action_dim = 8
SHOW = False
SHOW_LAST_EPOCH = False
TRAIN = False
LOAD_MODEL = False
EPOCHS = 300
board = Board(board_size)

# create the agents
agents: list[DQAgent] = [
    DQAgent(
        state_dim=state_dim, 
        action_dim=action_dim, 
        lr=1e-4,
        gamma=0.90,                    # Prioritize short-term rewards
        epsilon_decay=0.9998,           # Slower exploration decay
        memory_size=20000, 
        target_update_freq = 32
    ) for i in range(robot_count)
]

robots: list[list[Robot,Goal]] = [ create_random_agents(i+1,board_size) for i in range(robot_count)] # randomly innitilize robots
reward_dataset = [[0]*EPOCHS for i in range(robot_count)]
loss_dataset = [[0]*EPOCHS for i in range(robot_count)]
if SHOW:
    main_fig, ax1, axs = create_figure(robot_count)

for epoch in range(EPOCHS):
    
    board.players = []
    for i,[r,g] in enumerate(robots):
        a = agents[i]
        board.add_robot(r,g,a)

    # SHOW = epoch == EPOCHS-1
    # if SHOW:
    #     main_fig, ax1, axs = create_figure(robot_count)
    
    reset_positions(board.players, board_size)
    
    # 0. Initilize board
    board.update_robots()
    board.draw_board()
    board.update_views()
    # print("Step 0 done")

    # 1. get the states for each robot
    curr_states = []
    for i,[r,g,a] in enumerate(board.players):
        r.detect_robots()  # detect which robots are in the view
        for j in range(len(r.detected_robots['id'])):  #  give the robot information for those in the view 
            r.detected_robots["robot"][j] = board.get_robot_by_id(r.detected_robots['id'][j])
        curr_state = r.get_DQL_state(g)
        curr_states.append(curr_state)
    # print("Step 1 done")

    print("-"*100,epoch,"-"*100)
    logger.info(f'{"-"*100} {epoch} {"-"*100}')
    iter = 0
    iter_time_start = time.time()
    done = False
    while not done:
        # 2. choose their action
        actions = []
        for i,[r,g,a] in enumerate(board.players):
            action = a.choose_action(curr_states[i])
            actions.append(action)
            r._set_dir(action)
        # print("Step 2 done", actions, end=" ")

        # 3. update the board by moving the players based on the actions
        move_success = []
        for [r,g,a] in board.players:
            move_success.append (
                r.move(x_max=board_size, y_max=board_size)
            )
        # print("   Step 3 done", move_success)
        
        # 4. update the view and environment
        board.update_robots()
        board.draw_board()
        board.update_views()
        # print("Step 4 done")

        # 5. get the new states for each robot 
        new_states = []
        for i,[r,g,a] in enumerate(board.players):
            r.detect_robots()  # detect which robots are in the view

            for j in range(len(r.detected_robots['id'])):  #  give the robot information for those in the view
                r.detected_robots["robot"][j] = board.get_robot_by_id(r.detected_robots['id'][j])

            new_state = r.get_DQL_state(g)
            new_states.append(new_state)
        # print("Step 5 done")

        # 6. compute the reward
        rewards = []
        for i,[r,g,a] in enumerate(board.players):
            if not isinstance(reward_dataset[r.id-1][epoch],list):
                reward_dataset[r.id-1][epoch] = []
            reward = calculate_reward(r,g,move_success[i])
            rewards.append(reward)
            reward_dataset[r.id-1][epoch].append(reward)
        # print("Step 6 done", rewards)

        # 7. Store experience & train
        for i,[r,g,a] in enumerate(board.players):
            if not isinstance(loss_dataset[r.id-1][epoch],list):
                loss_dataset[r.id-1][epoch] = []
            done = (len(board.players) == 0)
            a.remember(curr_states[i], actions[i], rewards[i], new_states[i], done)
            loss = a.replay(batch_size=128)
            loss_dataset[r.id-1][epoch].append(loss)

        if iter > 3000 or (len(board.players) == 0):
            done = True

        #     print("loss: ",i,loss)
        # print("Step 7 done")

        # 8. update the current_states with new_states
        curr_states = new_states
        iter += 1
        # print("Step 8 done")
        # print(iter, len(board.players))
        if SHOW:
            for [r,g,a] in board.players:
                # axs[r.id-1].imshow(r.view, vmin=-robot_count, vmax=robot_count)
                axs[r.id-1].plot(range(iter)[-100:],loss_dataset[r.id-1][epoch][-100:])
                axs[r.id-1].plot(range(iter)[-100:],reward_dataset[r.id-1][epoch][-100:])
                axs[r.id-1].set_title(f"{r.id}\n"+','.join(map(str,r.detected_robots['id'])))
                ax1.imshow(board.board, vmin=-robot_count, vmax=robot_count)
            plt.pause(0.5)
            for [r,g,a] in board.players:
                axs[r.id-1].cla()
            ax1.cla()
        # print("-"*50)
    iter_time_end = time.time()

    loss_r = []
    reward_r = []
    for i in range(len(loss_dataset)):
        # Replace None values with np.nan
        mean_list_loss = [val if val is not None else np.nan for val in loss_dataset[i][epoch]]
        mean_list_reward = [val if val is not None else np.nan for val in reward_dataset[i][epoch]]
        
        # Avoid empty lists by checking the length before calculating the mean
        if len(mean_list_loss) > 0 and not all(np.isnan(val) for val in mean_list_loss):
            loss_r.append(np.nanmean(mean_list_loss))  # Use np.nanmean to ignore np.nan values
        else:
            loss_r.append(np.nan)  # Append np.nan if the list is empty or only contains np.nan values
        
        if len(mean_list_reward) > 0 and not all(np.isnan(val) for val in mean_list_reward):
            reward_r.append(np.nanmean(mean_list_reward))  # Use np.nanmean to ignore np.nan values
        else:
            reward_r.append(np.nan)

    print(f"iter: {iter}\ttime per iter: {(iter_time_end-iter_time_start)/iter:.4f}\tEpoch time: {(iter_time_end-iter_time_start):.2f}\taverage_loss: {loss_r}\taverage_reward: {reward_r}")
    logger.info(f"iter: {iter}\ttime per iter: {(iter_time_end-iter_time_start)/iter:.4f}\tEpoch time: {(iter_time_end-iter_time_start):.2f}\taverage_loss: {loss_r}\taverage_reward: {reward_r}")
