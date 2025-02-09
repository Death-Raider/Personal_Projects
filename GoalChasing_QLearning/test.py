from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
import matplotlib.pyplot as plt
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
        print(r1.get_dist([g1.y,g1.x])[0])
    return [r1,g1]

robot_count = 10
board_size = 20

board = Board(board_size)

robots: list[list[Robot,Goal]] = [ create_random_agents(i+1,board_size) for i in range(robot_count)]
for [r,g] in robots:
    print(r.v, r.x,r.y, " --- ", g.x, g.y )
    board.add_robot(r,g)

plt.ion()
while len(board.players) > 0:
    board.update_robots()
    board.update_dist_table()
    board.draw_board()

    for i,[r,g] in enumerate(board.players):
        # print("robot:",i , r.v, r.dir, r.x, r.y)
        r.set_dir(g,board.dist_table[i,:])
        # print("robot:",i , r.v, r.dir, r.x, r.y)
        r.move()
    # print(board.dist_table)
    plt.imshow(board.board)
    plt.pause(0.4)
plt.show()
plt.ioff()
