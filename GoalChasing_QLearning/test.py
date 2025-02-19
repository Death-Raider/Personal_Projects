from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def create_random_agents(id,board_size)->list[Robot,Goal]:
    r1 = Robot(id = id)
    g1 = Goal(id = id)

    r1.set_random_init_state(board_size, board_size)
    r1.v = 2
    g1.set_random_goal(board_size, board_size)
    print(r1.get_dist([g1.y,g1.x])[0])
    while r1.get_dist([g1.y,g1.x])[0] < board_size*0.50:
        g1.set_random_goal(board_size, board_size)
    return [r1,g1]

robot_count = 4
board_size = 20

board = Board(board_size)

robots: list[list[Robot,Goal]] = [ create_random_agents(i+1,board_size) for i in range(robot_count)]
for [r,g] in robots:
    print( r.x,r.y, " ---> ", g.x, g.y )
    board.add_robot(r,g)

plt.ion()

main_fig = plt.figure(figsize=(10,8))
gs = gridspec.GridSpec(2,3,height_ratios=[1,1],width_ratios=[1,1,1])
ax1 = main_fig.add_subplot(gs[:2,0]) # main images
axs = [
    main_fig.add_subplot(gs[0,1]),
    main_fig.add_subplot(gs[0,2]),
    main_fig.add_subplot(gs[1,1]),
    main_fig.add_subplot(gs[1,2])
]

while len(board.players) > 0:
    board.update_robots()
    board.draw_board()
    board.update_views()
    for i,[r,g] in enumerate(board.players):
        # print("robot:",i , r.v, r.dir, r.x, r.y)
        r.detect_robots()
        for i in range(len(r.detected_robots['id'])):
            r.detected_robots["robot"][i] = board.get_robot_by_id(r.detected_robots['id'][i])
        r.set_dir(g)
        axs[r.id-1].imshow(r.view, vmin=-4, vmax=4)
        axs[r.id-1].set_title(str(r.id))
        # print("robot:",i , r.v, r.dir, r.x, r.y)
        r.move()
    print("-"*50)
    ax1.imshow(board.board, vmin=-4, vmax=4)
    plt.pause(5)
plt.show()
plt.ioff()
