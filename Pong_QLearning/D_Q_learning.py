"""
Deep Q Learning Pong AI

- Uses Deep Q Learning instead of a Q-table for handling large state spaces
- Experience Replay for stable training
- Epsilon Decay for better exploration-exploitation balance

Environment:
    - board size
    - paddle size
    - ball size

State Space:
    - Position of player paddle (y1)
    - Position of opponent paddle (y2)
    - Position of ball (bx, by)
    - Direction of ball (angle)

"""

import numpy as np
import keyboard
import matplotlib.pyplot as plt
import time
import random
from collections import deque
from Environments.Pong.board import Board
from Agents.DQAgent import DQAgent  # Updated agent import
import tensorflow as tf
import keras

print(tf.__version__)

# Board settings
BOARD_SIZE = 40
PADDLE_LENGTH = 10
SHOW = False
board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)
board.reset_ball()

# Define state & action space
max_val = [BOARD_SIZE-PADDLE_LENGTH,BOARD_SIZE-PADDLE_LENGTH,BOARD_SIZE,BOARD_SIZE,360]
state_dim = 5  # (y1, y2, bx, by, a)
n_actions = 3  # idle, down, up

# Hyperparameters
learning_rate = 0.1
discount_factor = 0.90
exploration_prob = 0.01  # Start with full exploration

# Initialize agents
agent1 = DQAgent(state_dim, n_actions, lr=learning_rate, gamma=discount_factor, max_memory=1000)
agent2 = DQAgent(state_dim, n_actions, lr=learning_rate, gamma=discount_factor, max_memory=1000)

# agent1.q_network.model = keras.saving.load_model('Agent_1.keras') 
# agent2.q_network.model = keras.saving.load_model('Agent_2.keras') 

def normalize_board(state,vals):
    new_state = state.copy()
    for i in range(len(new_state)):
        new_state[i] /= vals[i]
    return new_state

# Training settings
epochs = 1000
reward_history = np.zeros((epochs, 3))
plt.ion()
for epoch in range(epochs):
    board.reset_score()
    board.reset_ball()

    # Get initial state
    board_state = board.current_board_state()
    board_state = normalize_board(board_state, max_val)

    current_state = np.array(board_state, dtype=np.float32)
    board.update()
    iterations = 0
    start_time = time.time()

    while True:
        score = board.get_board_score()
        if score[1] + score[2] > 20:
            break

        # Choose actions
        action1 = agent1.get_action(current_state)
        action2 = agent2.get_action(current_state)

        # Simulate environment step
        board.do_board_action(player=1, action=action1)
        board.do_board_action(player=2, action=action2)

        # Get new state
        board_state_new = board.current_board_state()
        board_state_new = normalize_board(board_state_new, max_val)

        next_state = np.array(board_state_new, dtype=np.float32)
        board.update()

        # Compute rewards
        reward1 = (
            0.1 * (score[1] - score[2])
            + 2 * (abs(board.ball.y - board.l_paddle.y) < PADDLE_LENGTH // 2)
            + (2 if board.l_paddle.y < board.ball.y < board.l_paddle.y + PADDLE_LENGTH else -2)
        )

        reward2 = (
            0.1 * (score[2] - score[1])
            + 2 * (abs(board.ball.y - board.r_paddle.y) < PADDLE_LENGTH // 2)
            + (2 if board.r_paddle.y < board.ball.y < board.r_paddle.y + PADDLE_LENGTH else -2)
        )

        reward_history[epoch, 0] += reward1
        reward_history[epoch, 1] += reward2

        # Store experience & train
        agent1.remember(current_state, action1, reward1, next_state, done=False)
        agent2.remember(current_state, action2, reward2, next_state, done=False)
        
        # if iterations % 10 == 0 and iterations != 0:
        agent1.train_step(batch_size=10)
        agent2.train_step(batch_size=10)

        # Update state
        current_state = next_state
        board.ball.move(board.l_paddle, board.r_paddle, board)
        if SHOW:
            plt.imshow(board.board, cmap="gray")
            plt.title(f"Scores - Left: {score[1]} | Right: {score[2]}")
            plt.pause(0.01)
            if keyboard.is_pressed('q'):
                plt.show()
                break
            # print(board.current_board_state())
            plt.clf()
        iterations += 1

    end_time = time.time()
    reward_history[epoch] /= iterations
    reward_history[epoch, 2] = end_time - start_time

    print(epoch, " time(ms): {0:.2f}".format(1000 * (end_time - start_time)))
    np.save("reward_history_over_epoch", reward_history)

np.save("reward_history_over_epoch", reward_history)
agent1.q_network.model.predict(np.array([[0,0,1,1,0]]))
agent2.q_network.model.predict(np.array([[0,0,1,1,0]]))
agent1.q_network.model.save("Agent_1.keras")
agent2.q_network.model.save("Agent_2.keras")
