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


# ============ Optional: Custom Callbacks ============
def training_callback(board, agents:dict[str,DQAgent], step, epoch):
    """Called every step during training"""
    # Implemented Epsilon Decay
    i = 0
    agents[f'agent{i+1}'].epsilon *= agents[f'agent{i+1}'].epsilon_decay
    agents[f'agent{i+1}'].epsilon = min(agents[f'agent{i+1}'].epsilon, agents[f'agent{i+1}'].epsilon_min)

    assert agents['agent1'].epsilon == agents['agent2'].epsilon, "different agent objects"

def epoch_callback(board, agents, epoch, metrics):
    """Called after each epoch"""
    avg_reward = np.mean([r[f'agent{i+1}'] for r in metrics['rewards'][-10:] for i in range(num_robots)])
    episode_length = np.mean(metrics['episode_lengths'][-10:])
    print(f"Epoch {epoch}: Avg Reward = {avg_reward:.2f}, Avg Episode Length = {episode_length:.0f}")

# Create 3 agents with SAME architecture, different action selection
agents_configs = {
    'DQN (Greedy)': DQAgent(state_dim, action_dim),
    'CADRL-Style': CADRLStyleAgent(state_dim, action_dim, num_action_samples=8)
}

results = {}

for name, agent in agents_configs.items():
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    # Create fresh environment
    board = Board(size=board_size)
    agents = {}
    for i in range(num_robots):
        robot = Robot(id=i+1, h=1, w=1, view_threshold=10, closeness_threshold=3)
        goal = Goal(id=i+1)
        robot.set_random_init_state(board_size, board_size)
        robot.v = 1
        goal.set_random_goal(board_size, board_size)
        while robot.get_dist(goal)[0] < board_size * 0.5:
            goal.set_random_goal(board_size, board_size)
        board.add_robot(robot, goal, None)
        agents[f'agent{i+1}'] = agent
    
    env = GoalChasingEnvironment(board, agents)
    runner = GameRunner(env)
    
    metrics = runner.run(
        epochs=100,
        max_steps_per_episode=1000,
        reward_functions=None,  # Use default reward function
        termination_condition=None,  # Use default termination
        step_callback=training_callback,
        episode_callback=epoch_callback,
        render=False,
        render_last_epoch=False,
        save_metrics=True,
        save_models=True,
        save_directory=f'./Runners/GoalChasing_QLearning/results/{name.replace(" ", "_")}',
        verbose=2
    )
    results[name] = metrics

