# import the environment 
from Environments.Pong.board import Board
from Environments.Pong.ball import Ball
from Environments.Pong.paddle import Paddle

# import the agent
from Agents.QAgent import QAgent

#import the Runner
import Pong_QLearning.Q_learning as pong_ql


board = Board(size=100, paddle_length=10)

pong_ql.run_game(
    Board, 
    agents={
        'agent1':pong_ql.agent1, 
        'agent2':pong_ql.agent2
    },
    epochs=1000, 
    SHOW_LAST_EPOCH=True, 
    SAVE_METRICS=True, 
    reward_functions={
        'reward_function1': pong_ql.reward_function,
        'reward_function2': pong_ql.reward_function
    }
)