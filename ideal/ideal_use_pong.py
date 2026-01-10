# ideal way our framework could be used to create a new Pong environment with obstacles

from Environments.Pong.board import Board
from Environments.Pong.ball import Ball
from Environments.Pong.paddle import Paddle

from Agents.QAgent import QAgent
from Agents.DQAgent import DQAgent

import Pong_QLearning.Q_learning as pong_ql

import time

new_board_type = Board(size=60, paddle_length=15, paddle_pos=22,)
obstacles = [(30,30),(31,30),(32,30),(33,30),(34,30),(35,30),
            (30,31),(31,31),(32,31),(33,31),(34,31),(35,31)]
obstacle_value = 999
for (ox,oy) in obstacles:
    new_board_type.board[oy][ox] = obstacle_value


new_ball_type = Ball(r=2, vel=1, dir=[0.5, 0.5])
def new_ball_physics_obj():
    # custom logic for ball movement for new obstacles
    pass

new_ball_type.move = new_ball_physics_obj

new_board_type.ball = new_ball_type

agent1 = pong_ql.agent1 # DQAgent
agent2 = DQAgent(
    state_dim=pong_ql.agent2.state_dim,
    action_dim=pong_ql.agent2.action_dim,
    lr=0.8,
    gamma=0.90,
    epsilon_decay=0.9998,
    memory_size=20000,
    target_update_freq=1000,
)

reward_function1 = pong_ql.Q_learning_reward_function

def reward_function2():
    pass

pong_ql.run_game(
    new_board_type, 
    agents={
        'agent1':agent1, 
        'agent2':agent2
    },
    epochs=1000, 
    SHOW_LAST_EPOCH=True, 
    SAVE_METRICS=True, 
    reward_functions={
        'reward_function1': reward_function1,
        'reward_function2': reward_function2
    }
)