from Environments.Pong.board import Board
from Environments.Pong.pong_env import PongEnvironment
from Agents.DQAgent import DQAgent
from Agents.QAgent import QAgent
from GameRunner import GameRunner

# Default configuration
BOARD_SIZE = 40
PADDLE_LENGTH = 10

# Create default board
default_board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)

# Create default agents
n_states = 5
n_actions = 3

q_n_states = (BOARD_SIZE - PADDLE_LENGTH + 1) ** 2 * (BOARD_SIZE+1) ** 2 * 361

agent1 = DQAgent(n_states, n_actions, lr=0.1, epsilon_decay=0.995, memory_size=20000, target_update_freq=100, epsilon=0.1)
agent2 = QAgent(q_n_states, n_actions, learning_rate=0.2, discount_factor=0.90, exploration_prob=0.10)

def build_model(state_dim,action_dim):
    from keras.layers import Dense, Input, LayerNormalization
    from keras.models import Model

    inputs = Input(shape=(state_dim,))
    x = Dense(100, activation='linear')(inputs)
    x = LayerNormalization()(x)
    x = Dense(100, activation='linear')(x)
    outputs = Dense(action_dim, activation='linear')(x)
    return Model(inputs=inputs, outputs=outputs)

agent1.build_model = build_model
agent1.initlize_models()

def run_game(board, agents, epochs=100, SHOW_LAST_EPOCH=False, SAVE_METRICS=False, 
             reward_functions=None, **kwargs):
    """
    Backward-compatible run function
    """
    # Create environment
    env = PongEnvironment(board, agents, config={'board_size': board.size, 'paddle_length': PADDLE_LENGTH, 'state_encoding': 'continuous'})
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