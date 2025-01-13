""" 
Q Learning

- has a Q leaning matrix with column as available action and row as a state
- Q-table is updated based on the agent's experiences
- Policy / Reward based updation
- Deep Q Learning can be used to work on continious states

Environment:
    - board size: 100 x 100
    - paddle size: 10 x 1
    - ball size: 1 x 1

Factors:
    - position of self paddle (y1): 90
    - position of opponent paddle (y2): 90
    - position of ball (bx,by): 100 x 100 = 10000
    - direction of ball (angle): 360

Reward Conditions: 
    - ball is successfully sent away
    - ball is sent to position away from opponent's paddle

Sources:
    - https://ai.stackexchange.com/questions/12255/can-q-learning-be-used-for-continuous-state-or-action-spaces
    - https://digitalcommons.wcupa.edu/cgi/viewcontent.cgi?article=1307&context=all_theses
    - https://www.geeksforgeeks.org/q-learning-in-python/ 
"""
import numpy as np
import keyboard
import matplotlib.pyplot as plt
import time

from QAgent import QAgent
from board import Board

BOARD_SIZE = 40
PADDLE_LENGTH = 10

board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)
board.reset_ball()

base_y1 = BOARD_SIZE - PADDLE_LENGTH+1
base_y2 = BOARD_SIZE - PADDLE_LENGTH+1
base_bx = BOARD_SIZE+1
base_by = BOARD_SIZE+1
base_a = 360

def state_to_index(y1, y2, bx, by, a): # (LSB to MSB) -> index
    return (y1 
            + y2 * base_y1 
            + bx * base_y1 * base_y2 
            + by * base_y1 * base_y2 * base_bx 
            + a * base_y1 * base_y2 * base_bx * base_by)

def index_to_state(index): # index -> (LSM to MSB)
    y1 = index % base_y1
    y2 = (index // base_y1) % base_y2
    bx = (index // (base_y1 * base_y2)) % base_bx
    by = (index // (base_y1 * base_y2 * base_bx)) % base_by
    a = index // (base_y1 * base_y2 * base_bx * base_by)
    
    return (y1, y2, bx, by, a)


n_states = base_y1*base_y2*base_bx*base_by*base_a
n_actions = 3 # idle and down and up
learning_rate = 0.8
discount_factor = 0.90
exploration_prob = 0.90

agent1 = QAgent(n_states, n_actions, learning_rate, discount_factor, exploration_prob)
agent2 = QAgent(n_states, n_actions, learning_rate, discount_factor, exploration_prob)
plt.ion()
epochs = 3000
reward_history = np.zeros((epochs,3))

for epoch in range(epochs):
    board.reset_score()
    board.reset_ball()

    board_state = board.current_board_state()
    current_state = state_to_index(*board_state)
    board.update()
    iterations = 0
    start_time = time.time()
    while True:
        score = board.get_board_score()
        if score[1]+score[2] > 20:
            break
        # choose an action
        try:
            action1 = agent1.choose_action(current_state)
            action2 = agent2.choose_action(current_state)
        except:
            action1 = np.random.randint(0,3)
            action2 = np.random.randint(0,3)
        # Simulate the environment based on action
        board.do_board_action(player=1, action=action1)
        board.do_board_action(player=2, action=action2)
        
        # get the new state
        board_state_new = board.current_board_state()
        next_state = state_to_index(*board_state_new)
        board.update()

        # calculate basic
        reward1 = 0.1*(score[1]-score[2]) \
            + 2 * (abs(board.ball.y - board.l_paddle.y) < PADDLE_LENGTH // 2) \
            + 2 if board.l_paddle.y < board.ball.y < board.l_paddle.y+PADDLE_LENGTH else -2
        
        reward2 = 0.1*(score[2]-score[1]) \
            + 2 * (abs(board.ball.y - board.r_paddle.y) < PADDLE_LENGTH // 2) \
            + 2 if board.r_paddle.y < board.ball.y < board.r_paddle.y+PADDLE_LENGTH else -2
        
        reward_history[epoch,0] += reward1
        reward_history[epoch,1] += reward2
        
        # update q-table
        try:
            agent1.update_q_value(current_state, action1, reward1, next_state)
            agent2.update_q_value(current_state, action2, reward2, next_state)
        except:
            pass
        current_state = next_state  # Move to the next state
        
        board.ball.move(board.l_paddle, board.r_paddle, board)
        if epoch == epochs-1:
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
    reward_history[epoch,2] = end_time - start_time
    agent1.exploration_prob -= 0.001
    agent1.exploration_prob = max(0.01,agent1.exploration_prob)
    agent2.exploration_prob = agent1.exploration_prob
    print(epoch, " time(ms):",1000*(end_time-start_time), " explora_prob:",agent1.exploration_prob)

np.save("reward_history_over_epoch",reward_history)
