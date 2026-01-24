"""
Compare DQN vs CADRL-style action selection
Same network architecture, different action choice
"""

from Environments.GoalChasing.goal_chasing_env import GoalChasingEnvironment
from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
from Agents.DQAgent import DQAgent
from Agents.CADRLAgent import CADRLStyleAgent
from GameRunner import GameRunner

import numpy as np
import logging

logging.basicConfig(
    filename='./Runners/GoalChasing_QLearning/results/train.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='w'
    )

# ======= Curriculum Learning Setup =======
INDEX = [0,1,2,3,4,5,6,7,8,9]
ROBOT_COUNTS = [10,20,30,10,20,40,10,20,30,50]
BOARD_SIZES = [50,100,100,40,60,100,40,50,60,100]
LEARNING_RATES = [1e-3,1e-4,1e-5,1e-3,1e-4,1e-5,1e-3,1e-4,1e-4,1e-5]
INITIAL_EPSILONS = [1,0.4,0.2,0.4,0.2,0.1,0.4,0.2,0.1,0.05]
EPOCHS = [40,60,50,40,60,50,40,60,50,50]

start_index = 0
end_index = 3
INDEX = INDEX[start_index:end_index]
ROBOT_COUNTS = ROBOT_COUNTS[start_index:end_index]
BOARD_SIZES = BOARD_SIZES[start_index:end_index]
LEARNING_RATES = LEARNING_RATES[start_index:end_index]
INITIAL_EPSILONS = INITIAL_EPSILONS[start_index:end_index]
EPOCHS = EPOCHS[start_index:end_index]

state_dim = (2 * 10 + 1) ** 2 * 2 + 2
action_dim = 8

def training_callback(board:Board, agents:dict[str,DQAgent], step:int, epoch:int, runner:GameRunner):
    """Called every step during training"""
    # Implemented Epsilon Decay
    i = 0
    agents[f'agent{i+1}'].epsilon *= agents[f'agent{i+1}'].epsilon_decay
    agents[f'agent{i+1}'].epsilon = max(agents[f'agent{i+1}'].epsilon, agents[f'agent{i+1}'].epsilon_min)

    # Adding Custom metrics
    info = runner.env.get_info()    
    all_collisions = [info['robots'].get(e,{'collisions':None})['collisions'] for e in range(1,num_robots+1)]
    runner.metrics['custom_metrics']['collisions'][epoch].append(all_collisions)
    runner.metrics['custom_metrics']['epsilon'][epoch].append(agents[f'agent{i+1}'].epsilon)

    assert agents['agent1'].epsilon == agents['agent2'].epsilon, "different agent objects"

def epoch_callback(board, agents, epoch, metrics, runner):
    """Called after each epoch"""
    avg_reward = np.mean([r[f'agent{i+1}'] for r in metrics['rewards'][-10:] for i in range(num_robots)])
    episode_length = np.mean(metrics['episode_lengths'][-10:])

    runner.metrics['custom_metrics'].setdefault('avg_reward', []).append(avg_reward)
    runner.metrics['custom_metrics'].setdefault('avg_episode_length', []).append(episode_length)
    logging.debug(runner.metrics)

agents_configs = {
    'DQN (Greedy)': DQAgent(
        state_dim, 
        action_dim,
        epsilon_decay=0.9998, 
        epsilon_min=0.01,
        target_update_freq=1000,
        memory_size=20000,
        ),
    'CADRL-Style': CADRLStyleAgent(
        state_dim, 
        action_dim, 
        epsilon_decay=0.9998, 
        epsilon_min=0.01,
        target_update_freq=1000,
        memory_size=20000,
        num_action_samples=8
        )
}

if start_index != 0:
    agents_configs['DQN (Greedy)'].load_model(f'./Runners/GoalChasing_QLearning/results/DQN_(Greedy)_{start_index-1}')
    agents_configs['CADRL-Style'].load_model(f'./Runners/GoalChasing_QLearning/results/CADRL-Style_{start_index-1}')

for indx,num_robots,board_size,lr,init_eps,epochs in zip(INDEX,ROBOT_COUNTS,BOARD_SIZES,LEARNING_RATES,INITIAL_EPSILONS,EPOCHS):

    logging.info(f"\n{'#'*80}\nCurriculum Step {indx+1}/10: {num_robots} Robots, Board Size: {board_size}x{board_size}, LR: {lr}, Init Eps: {init_eps}, Epochs: {epochs}\n{'#'*80}\n")

    agents_configs['DQN (Greedy)'].learning_rate = lr
    agents_configs['DQN (Greedy)'].epsilon = init_eps

    agents_configs['CADRL-Style'].learning_rate = lr
    agents_configs['CADRL-Style'].epsilon = init_eps

    board_config = {
        'board_size': board_size,
        'view_threshold': 10,
        'closeness_threshold': 3,
        'num_robots': num_robots,
        'reset_on_goal': True  # Remove robot when goal reached
    }

    results = {}

    for name, agent in agents_configs.items():
        logging.info(f"\n{'='*60}")
        logging.info(f"Training: {name}")
        logging.info('='*60)
        
        # Create fresh environment
        board = Board(size=board_size)
        board.max_players = num_robots
        agents = {}
        for i in range(num_robots):
            agents[f'agent{i+1}'] = agent
        
        env = GoalChasingEnvironment(board, agents, config=board_config)
        env.add_robots()
        runner = GameRunner(env)
        runner.metrics['custom_metrics']['epsilon'] = [[] for _ in range(epochs)]
        runner.metrics['custom_metrics']['collisions'] = [[] for _ in range(epochs)]
        
        metrics = runner.run(
            epochs=epochs,
            max_steps_per_episode=1000,
            reward_functions=None,  # Use default reward function
            termination_condition=None,  # Use default termination
            step_callback=training_callback,
            episode_callback=epoch_callback,
            render=False,
            render_last_epoch=False,
            save_metrics=True,
            save_models=True,
            save_directory=f'./Runners/GoalChasing_QLearning/results/{name.replace(" ", "_")}_{indx}',
            verbose=2,
            train=True
        )
        # results[name] = metrics

