from Environments.Pong_obs.board import Board
from Environments.Pong_obs.pong_env import PongEnvironment
from Agents.QAgent import QAgent
from GameRunner import GameRunner

# Default configuration
BOARD_SIZE = 40
PADDLE_LENGTH = 10

# Create default board
default_board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)

# Create default agents
# State space: [paddle1_y, paddle2_y, ball_y, ball_x, ball_angle]
n_states = (BOARD_SIZE - PADDLE_LENGTH + 1) ** 2 * (BOARD_SIZE+1) ** 2 * 360
n_actions = 3

agent1 = QAgent(n_states, n_actions, learning_rate=0.5, discount_factor=0.90, exploration_prob=0.10)
agent2 = QAgent(n_states, n_actions, learning_rate=0.5, discount_factor=0.90, exploration_prob=0.10)

def run_game(board, agents, epochs=1000, SHOW_LAST_EPOCH=False, SAVE_METRICS=False, 
             reward_functions=None, **kwargs):
    # Create environment
    env = PongEnvironment(board, agents, config={'board_size': board.size, 'paddle_length': PADDLE_LENGTH, 'state_encoding': 'discrete'}, )
    assert env.n_states == n_states, f"State size mismatch! Expected {n_states}, got {env.n_states}"
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