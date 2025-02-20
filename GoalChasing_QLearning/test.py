from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
from Agents.DQAgent import DQAgent
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

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
        print(r.get_dist(g)[0])
        while r.get_dist(g)[0] < board_size*0.50:
            g.set_random_goal(board_size, board_size)

robot_count = 4
board_size = 20
threshold = 3
state_dim = (2*threshold+1) * (2*threshold+1) * 2
action_dim = 360
SHOW = True
EPOCHS = 10
board = Board(board_size)

# create the agents
agents: list[DQAgent] = [DQAgent(state_dim=state_dim, action_dim=action_dim, lr=1e-3) for i in range(robot_count)]
for a in agents:
    a.create_model()

robots: list[list[Robot,Goal]] = [ create_random_agents(i+1,board_size) for i in range(robot_count)] # randomly innitilize robots

# add the robots
for i,[r,g] in enumerate(robots):
    print( r.x,r.y, " ---> ", g.x, g.y )
    a = agents[i]
    board.add_robot(r,g,a)

for epoch in range(EPOCHS):
    board.players = []
    for i,[r,g] in enumerate(robots):
        print( r.x,r.y, " ---> ", g.x, g.y )
        a = agents[i]
        board.add_robot(r,g,a)
    SHOW = epoch == EPOCHS-1
    reset_positions(board.players, board_size)

    if SHOW:
        # plt.ion()
        plt.figure()
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
        curr_state = r.get_DQL_state()
        curr_states.append(curr_state)
    # print("Step 1 done")
    print("-"*100,epoch,"-"*100)
    iter = 0
    while (len(board.players) > 0) and (iter < 100):

        # 2. choose their action
        actions = []
        for i,[r,g,a] in enumerate(board.players):
            action = a.choose_action(curr_states[i])
            actions.append(action)
            r.dir = action*np.pi/180
        # print("Step 2 done", actions)

        # 3. update the board by moving the players based on the actions
        move_success = []
        for [r,g,a] in board.players:
            move_success.append (
                r.move(x_max=board_size, y_max=board_size)
            )
        # print("Step 3 done")
        
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
            new_state = r.get_DQL_state()
            new_states.append(new_state)
        # print("Step 5 done")

        # 6. compute the reward
        rewards = []
        for i,[r,g,a] in enumerate(board.players):
            pos = r.get_dist(g)
            reward = 5/(5*pos[0]+0.1) + (1 if move_success[i] else -5) + (1 if r.dir-0.05<=pos[1]<=r.dir+0.01 else -2)
            rewards.append(reward)
        # print("Step 6 done", rewards)

        # 7. Store experience & train
        for i,[r,g,a] in enumerate(board.players):
            a.store_transition(curr_states[i], actions[i], rewards[i], new_states[i])
            loss = a.update_model(batch_size=32, fit=False)
            # print("loss: ",i,loss)
        # print("Step 7 done")

        # 8. update the current_states with new_states
        curr_states = new_states
        iter += 1
        # print("Step 8 done")
        # print(iter, len(board.players))
        if SHOW:
            plt.imshow(board.board,vmax=4,vmin=-4)
            plt.pause(0.5)
        # print("-"*50)
    plt.show()
    plt.ioff()


"""
PLT CODE:
main_fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2,3,height_ratios=[1,1],width_ratios=[1,1,1])
ax1 = main_fig.add_subplot(gs[:2,0]) # main images
axs = [
    main_fig.add_subplot(gs[0,1]),
    main_fig.add_subplot(gs[0,2]),
    main_fig.add_subplot(gs[1,1]),
    main_fig.add_subplot(gs[1,2])
]
axs[r.id-1].imshow(r.view, vmin=-4, vmax=4)
axs[r.id-1].set_title(f"{r.id}\n"+','.join(map(str,r.detected_robots['id'])))
ax1.imshow(board.board, vmin=-4, vmax=4)
plt.show()
"""