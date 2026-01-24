# 1. load the trained model
# 2. generate multiple sized environments
# 3. evaluate collision rates across different scenarios by counting all collisions and dividing by total steps in episode

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

# Setup
board_size = 100
num_robots = 10
state_dim = (2 * 10 + 1) ** 2 * 2 + 2
action_dim = 8

Collison_Data_Matrix = []
# ============ Optional: Custom Callbacks ============
def training_callback(board:Board, agents:dict[str,DQAgent], step:int, epoch:int, runner:GameRunner):
    """Called every step during training"""
    info = runner.env.get_info()
    # print(f"Step {step}, Epoch {epoch}:\n\t{info}\n")
    
    all_collisions = [info['robots'].get(e,{'collisions':0})['collisions'] for e in range(num_robots)]
    global Collison_Data_Matrix

    Collison_Data_Matrix.append(all_collisions)
# Create 3 agents with SAME architecture, different action selection

DQN_agent = DQAgent(state_dim, action_dim)
DQN_agent.load_model('./Runners/GoalChasing_QLearning/results/DQN_(Greedy)/agent1_epoch_final')
DQN_agent.epsilon = 0.0  # No exploration during evaluation
DQN_agent.epsilon_min = 0.0
DQN_agent.epsilon_decay = 0.0
DQN_agent.batch_size = 1  # No training during evaluation

CADRL_agent = CADRLStyleAgent(state_dim, action_dim, num_action_samples=8)
CADRL_agent.load_model('./Runners/GoalChasing_QLearning/results/CADRL-Style/agent1_epoch_final')
CADRL_agent.epsilon = 0.0  # No exploration during evaluation
CADRL_agent.epsilon_min = 0.0
CADRL_agent.epsilon_decay = 0.0
CADRL_agent.batch_size = 1  # No training during evaluation

agents_configs = {
    'CADRL-Style': CADRL_agent,
    'DQN (Greedy)': DQN_agent,
}

results = {}

for name, agent in agents_configs.items():
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    # Create fresh environment
    board = Board(size=board_size)
    board.max_players = num_robots
    agents = {}
    for i in range(num_robots):
        agents[f'agent{i+1}'] = agent
    
    env = GoalChasingEnvironment(board, agents)
    env.add_robots()
    runner = GameRunner(env)
    
    metrics = runner.run(
        epochs=5,
        max_steps_per_episode=200,
        reward_functions=None,  # Use default reward function
        termination_condition=None,  # Use default termination
        step_callback=training_callback,
        episode_callback=None,
        render=True,
        render_last_epoch=False,
        save_metrics=False,
        save_models=False,
        save_directory=f'./Runners/GoalChasing_QLearning/results/{name.replace(" ", "_")}',
        verbose=2,
        train=False
    )
    results[name] = metrics

    Collison_Data_Matrix = np.array(Collison_Data_Matrix)
    total_collisions_agent_wise = np.sum(Collison_Data_Matrix, axis=0) # Agent wise collisions across all epochs
    total_collisions_step_wise = np.sum(Collison_Data_Matrix, axis=1) # step wise collisions across all agents
    total_collisions = np.sum(total_collisions_agent_wise) # Total collisions across all agents and epochs

    print(f"Total Collisions for {name}:\nAgent Wise: {total_collisions_agent_wise}\nEpoch Wise: {total_collisions_step_wise}\nOverall: {total_collisions}")
    Collison_Data_Matrix = []