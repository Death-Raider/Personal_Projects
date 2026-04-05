from Environments.Pong_obs.board import Board
from Environments.Pong_obs.pong_env import PongEnvironment
from Agents.DQAgent import DQAgent
from GameRunner import GameRunner
from Runners.Pong_QLearning.model import model_fn

import numpy as np

def epsilon_decay_fn(epsilon, decay_rate=0.995, min_epsilon=0.01):
    return max(min_epsilon, epsilon * decay_rate)

def step_callback_ep_decay(board: Board, agents: dict[str, DQAgent], step: int, epoch: int, runner: GameRunner):

    if 'obs_state' not in runner.metrics['custom_metrics']:
        runner.metrics['custom_metrics']['obs_state'] = []

    state = board.current_board_state()
    if (state[-1] in (-1,1) or state[-2] in (-1,1)) and (state[4] not in (0,180)):
        runner.metrics['custom_metrics']['obs_state'].append({
            'step': step,
            'state': state
        })
    for agent in agents.values():
        agent.epsilon = epsilon_decay_fn(agent.epsilon, decay_rate=agent.epsilon_decay, min_epsilon=agent.epsilon_min)

def episode_callback_ep_reset(board: Board, agents: dict[str, DQAgent], epoch: int, metrics: dict, runner: GameRunner):
    if 'init_epsilon' not in runner.metrics['custom_metrics']:
        runner.metrics['custom_metrics']['init_epsilon'] = [(1,1) for _ in range(runner.epochs+1)]
    for agent in agents.values():
        agent.epsilon = np.random.uniform(0, 1-epoch/runner.epochs)
    runner.metrics['custom_metrics']['init_epsilon'][epoch+1] = tuple(agent.epsilon for agent in agents.values())


# Default configuration
BOARD_SIZE = 40
PADDLE_LENGTH = 10

# Create default board
default_board = Board(size=BOARD_SIZE, paddle_length=PADDLE_LENGTH, paddle_pos=5)

# Create default agents
n_states = 5+2
n_actions = 3

agent1 = DQAgent(n_states, n_actions, lr=0.5, epsilon_decay=0.995, memory_size=10000, target_update_freq=1000)
agent2 = DQAgent(n_states, n_actions, lr=0.5, epsilon_decay=0.995, memory_size=10000, target_update_freq=1000)

M1 = model_fn(n_states, n_actions)
M2 = model_fn(n_states, n_actions)

agent1.initlize_models(model=M1)
agent2.initlize_models(model=M2)

def run_game(board, agents, epochs=100, SHOW_LAST_EPOCH=False, SAVE_METRICS=False, 
             reward_functions=None, **kwargs):
    # Create environment
    env = PongEnvironment(board, agents, config={'board_size': board.size, 'paddle_length': PADDLE_LENGTH, 'state_encoding': 'continuous'})
    assert env.n_states == n_states, f"State size mismatch! Expected {n_states}, got {env.n_states}"
    # Create runner
    runner = GameRunner(env)
    
    # Run
    metrics = runner.run(
        epochs=epochs,
        reward_functions=reward_functions,
        render_last_epoch=SHOW_LAST_EPOCH,
        step_callback=step_callback_ep_decay,
        episode_callback=episode_callback_ep_reset,
        save_metrics=SAVE_METRICS,
        **kwargs
    )
    
    return metrics