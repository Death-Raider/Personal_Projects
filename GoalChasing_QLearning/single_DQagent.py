from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
from Agents.DQAgent import DQAgent
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import time
import logging
import os

logging.basicConfig(filename='GoalChasing_QLearning/output.log', filemode='a', level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('goal_chasing')

def create_random_agents(id,board_size,**kwargs)->list[Robot,Goal]:
    r1 = Robot(id = id, **kwargs)
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

def reward_policy(r: Robot, g: Goal, move_success: bool, collision_count: int, time: int) -> float:
    distance = r.get_dist(g)[0] # get_dist return [distance, angle(in radian)]
    angle_dir = r.DIR_ANGLES[r.dir]*np.pi/180

    angle_error = abs(r.get_dist(g)[1] - angle_dir) % (2*np.pi)
    
    # Primary reward components
    reward = 2 * (1/distance)  # Distance incentive
    reward += 4 if distance < 1.3 else 0  # Distance incentive
    reward += 5 * np.cos(angle_error)  # Direction alignment
    reward -= time*0.01  # Step penalty
    
    # Collision/behavior penalties
    if not move_success:
        reward -= 2
    if collision_count > 0:
        reward -= 2 * collision_count
    else:
        reward += 0.2
    # ---------- collision avoidance policy ----------------- #
    for i,r_o in enumerate(r.detected_robots['robot']):
        dist = r.detected_robots['pos'][i][0]
        if dist < r.closeness_threshold:
            reward -= 1.5 * (1 - dist / r.closeness_threshold)**2
        if dist > r.closeness_threshold * 1.5:
            reward += 0.2  # reward spacing

        ro_angle = r_o.DIR_ANGLES[r_o.dir]*np.pi/180
        angle_diff = np.abs(angle_dir - ro_angle) % (2*np.pi)
        reward += np.cos(angle_diff/2)**2
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

def save_model_and_data(agent, dir_path):
    print("Training completed.")

    if not os.path.exists(f"GoalChasing_QLearning/agents/"):
        os.makedirs(f"GoalChasing_QLearning/agents/")
    if not os.path.exists(f"GoalChasing_QLearning/agents/{dir_path}"):
        os.makedirs(f"GoalChasing_QLearning/agents/{dir_path}")

    agent.save_model(directory=f"GoalChasing_QLearning/agents/{dir_path}")

    states = np.array([t[0] for t in agent.memory], dtype=np.float32)
    actions = np.array([t[1] for t in agent.memory], dtype=np.int32)
    rewards = np.array([t[2] for t in agent.memory], dtype=np.float32)
    next_states = np.array([t[3] for t in agent.memory], dtype=np.float32)
    dones = np.array([t[4] for t in agent.memory], dtype=np.float32)
    print("Saving training data...")

    if not os.path.exists(f"GoalChasing_QLearning/training_data/"):
        os.makedirs(f"GoalChasing_QLearning/training_data/")
    if not os.path.exists(f"GoalChasing_QLearning/training_data/{dir_path}"):
        os.makedirs(f"GoalChasing_QLearning/training_data/{dir_path}")
        
    np.save(f"GoalChasing_QLearning/training_data/{dir_path}/curr_state.npy", states)
    np.save(f"GoalChasing_QLearning/training_data/{dir_path}/action.npy", actions)
    np.save(f"GoalChasing_QLearning/training_data/{dir_path}/reward.npy", rewards)
    np.save(f"GoalChasing_QLearning/training_data/{dir_path}/next_state.npy", next_states)
    np.save(f"GoalChasing_QLearning/training_data/{dir_path}/dones.npy",dones)

def load_model_and_data(agent, dir_path):
    agent.load_model(f"GoalChasing_QLearning/agents/{dir_path}")
    agent.update_target_network()
    print("Model loaded from", f"GoalChasing_QLearning/agents/{dir_path}")

    states =        np.load(f"GoalChasing_QLearning/training_data/{dir_path}/curr_state.npy", allow_pickle=True)
    actions =       np.load(f"GoalChasing_QLearning/training_data/{dir_path}/action.npy", allow_pickle=True)
    rewards =       np.load(f"GoalChasing_QLearning/training_data/{dir_path}/reward.npy", allow_pickle=True)
    next_states =   np.load(f"GoalChasing_QLearning/training_data/{dir_path}/next_state.npy", allow_pickle=True)
    dones =         np.load(f"GoalChasing_QLearning/training_data/{dir_path}/dones.npy", allow_pickle=True)

    agent.memory = [*zip(states, actions, rewards, next_states, dones)] # load to memory

    return states, actions, rewards, next_states, dones

def set_board(board):
    board.update_robots()
    board.draw_board()
    board.update_views()

def get_curr_state(board):
    curr_states = []
    for i,[r,g,a] in enumerate(board.players):
        r.detect_robots()  # detect which robots are in the view
        for j in range(len(r.detected_robots['id'])):  #  give the robot information for those in the view 
            r.detected_robots["robot"][j] = board.get_robot_by_id(r.detected_robots['id'][j])
        curr_state = r.get_DQL_state(g)
        curr_states.append(curr_state)
    return curr_states

def choose_action(board, curr_states):
    actions = []
    for i,[r,g,a] in enumerate(board.players):
        action = a.choose_action(curr_states[i])
        actions.append(action)
        r._set_dir(action)
    return actions

def move_robots(board, board_size):
    move_success = []
    for [r,g,a] in board.players:
        move_success.append (
            r.move(x_max=board_size, y_max=board_size)
        )
    return move_success

def get_new_states(board):
    new_states = []
    collisions = []
    for i,[r,g,a] in enumerate(board.players):
        collision_count = r.detect_robots()  # detect which robots are in the view
        collisions.append(collision_count)
        for j in range(len(r.detected_robots['id'])):  #  give the robot information for those in the view
            r.detected_robots["robot"][j] = board.get_robot_by_id(r.detected_robots['id'][j])
        new_state = r.get_DQL_state(g)
        new_states.append(new_state)
    return new_states, collisions

def get_reward(board, reward_dataset, move_success, collisions, epoch, iter):
    rewards = []
    for i,[r,g,a] in enumerate(board.players):
        if not isinstance(reward_dataset[r.id-1][epoch],list):
            reward_dataset[r.id-1][epoch] = []
        reward = reward_policy(r,g,move_success[i], collisions[i], iter)
        rewards.append(reward)
        reward_dataset[r.id-1][epoch].append(reward)
    return rewards

def get_update(board, loss_dataset, epoch, curr_states, actions, rewards, new_states, done, TRAIN=True):
    for i,[r,g,a] in enumerate(board.players):
        if not isinstance(loss_dataset[r.id-1][epoch],list):
            loss_dataset[r.id-1][epoch] = []
        done = (len(board.players) == 0)

        a.remember(curr_states[i], actions[i], rewards[i], new_states[i], done)
        if TRAIN:
            loss = a.replay(batch_size=128)
            loss_dataset[r.id-1][epoch].append(loss)
    return done

def game_loop(board, board_size, curr_states, iter, epoch, reward_dataset, loss_dataset, done, TRAIN=True):
    actions = choose_action(board, curr_states)
    move_success = move_robots(board, board_size)
    set_board(board)
    new_states, collisions = get_new_states(board)
    rewards = get_reward(board, reward_dataset, move_success, collisions, epoch, iter)
    done = get_update(board, loss_dataset, epoch, curr_states, actions, rewards, new_states, done, TRAIN)

    if iter > 3000 or (len(board.players) == 0):
        done = True
    curr_states = new_states
    iter += 1
    return iter, reward_dataset, loss_dataset, curr_states, actions, move_success, new_states, collisions, rewards, done

def game_plotting(board, ax1, axs, robot_count):
    for [r,g,a] in board.players:
        axs[r.id-1].imshow(r.view, vmin=-robot_count, vmax=robot_count)
        # axs[r.id-1].plot(range(iter)[-100:],loss_dataset[r.id-1][epoch][-100:])
        # axs[r.id-1].plot(range(iter)[-100:],reward_dataset[r.id-1][epoch][-100:])
        axs[r.id-1].set_title(f"{r.id}\n"+','.join(map(str,r.detected_robots['id'])))
        ax1.imshow(board.board, vmin=-robot_count, vmax=robot_count)
    plt.pause(0.5)
    for [r,g,a] in board.players:
        axs[r.id-1].cla()
    ax1.cla()

def run(board, threshold, robot_count, board_size, agent, EPOCHS, TRAIN=True, SHOW=False, SHOW_LAST_EPOCH=False, agent_directory=''):
    robots: list[list[Robot,Goal]] = [ create_random_agents(i+1,board_size,h=1,w=1,closeness_threshold=threshold//3, view_threshold=threshold) for i in range(robot_count)] # randomly innitilize robots
    reward_dataset = [[0]*EPOCHS for i in range(robot_count)]
    loss_dataset = [[0]*EPOCHS for i in range(robot_count)]

    if SHOW:
        main_fig, ax1, axs = create_figure(robot_count)

    for epoch in range(EPOCHS):
        print("-"*100,epoch,"-"*100)
        logger.info(f'{"-"*100} {epoch} {"-"*100}')
        
        # reset players for each epoch
        board.players = []
        for i,[r,g] in enumerate(robots):
            board.add_robot(r,g,agent)
        
        reset_positions(board.players, board_size)
        
        set_board(board)
        curr_states = get_curr_state(board)

        if (not SHOW) and SHOW_LAST_EPOCH and epoch == EPOCHS-1:
            main_fig, ax1, axs = create_figure(robot_count)
            game_plotting(board, ax1, axs, robot_count)        

        iter = 0
        iter_time_start = time.time()
        done = False

        while not done:
            iter, reward_dataset, loss_dataset, curr_states, \
            actions, move_success, new_states, collisions, rewards, done = game_loop(board, board_size, curr_states, iter, epoch, reward_dataset, loss_dataset, done, TRAIN)

            if SHOW or (SHOW_LAST_EPOCH and epoch == EPOCHS-1):
                game_plotting(board, ax1, axs, robot_count)

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

    save_model_and_data(agent, agent_directory)

    if SHOW or SHOW_LAST_EPOCH:
        plt.ioff()
        plt.show()

