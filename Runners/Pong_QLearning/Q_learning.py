""" 
Q Learning

- has a Q leaning matrix with column as available action and row as a state
- Q-table is updated based on the agent's experiences
- Policy / Reward based updation
- Deep Q Learning can be used to work on continious states

Environment:
    - board size
    - paddle size
    - ball size

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

from Environments.Pong.board import Board
from Environments.Pong.pong_env import PongEnvironment
from Agents.QAgent import QAgent
from GameRunner import GameRunner

# Default configuration
BOARD_SIZE = 40
PADDLE_LENGTH = 10

# Create default board
default_board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)

# Create default agents
n_states = (BOARD_SIZE - PADDLE_LENGTH + 1) ** 2 * (BOARD_SIZE+1) ** 2 * 360
n_actions = 3

agent1 = QAgent(n_states, n_actions, learning_rate=0.8, discount_factor=0.90, exploration_prob=0.10)
agent2 = QAgent(n_states, n_actions, learning_rate=0.8, discount_factor=0.90, exploration_prob=0.10)

def run_game(board, agents, epochs=1000, SHOW_LAST_EPOCH=False, SAVE_METRICS=False, 
             reward_functions=None, **kwargs):
    """
    Backward-compatible run function
    """
    # Create environment
    env = PongEnvironment(board, agents, config={'board_size': board.size, 'paddle_length': PADDLE_LENGTH})
    assert env.n_states == n_states, "State size mismatch!"
    # Create runner
    runner = GameRunner(env)
    
    # Run
    metrics = runner.run(
        epochs=epochs,
        reward_functions=reward_functions,
        render_last_epoch=SHOW_LAST_EPOCH,
        save_metrics=SAVE_METRICS,
        **kwargs
    )
    
    return metrics