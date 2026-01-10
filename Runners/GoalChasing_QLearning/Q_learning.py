# examples/goal_chasing_basic.py
"""
Basic Goal Chasing example using the new framework
Demonstrates multi-agent navigation with collision avoidance
"""

from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal
from Environments.GoalChasing.goal_chasing_env import GoalChasingEnvironment
from Agents.DQAgent import DQAgent
from GameRunner import GameRunner

import numpy as np

# ============ Configuration ============
BOARD_SIZE = 50
NUM_ROBOTS = 5
VIEW_THRESHOLD = 10
CLOSENESS_THRESHOLD = 3
EPOCHS = 3

# ============ Setup Board ============
print("Creating Goal Chasing environment...")
board = Board(size=BOARD_SIZE)

# ============ Create Robots and Goals ============
print(f"Creating {NUM_ROBOTS} robots with goals...")

robots_and_goals = []
for i in range(NUM_ROBOTS):
    # Create robot
    robot = Robot(
        id=i + 1,
        h=1,
        w=1,
        closeness_threshold=CLOSENESS_THRESHOLD,
        view_threshold=VIEW_THRESHOLD
    )
    
    # Create goal
    goal = Goal(id=i + 1)
    
    # Random initialization
    robot.set_random_init_state(BOARD_SIZE, BOARD_SIZE)
    robot.v = 1
    goal.set_random_goal(BOARD_SIZE, BOARD_SIZE)
    
    # Ensure goal is far from robot
    while robot.get_dist(goal)[0] < BOARD_SIZE * 0.5:
        goal.set_random_goal(BOARD_SIZE, BOARD_SIZE)
    
    robots_and_goals.append((robot, goal))

# Add robots to board
for robot, goal in robots_and_goals:
    board.add_robot(robot, goal, None)  # Agent will be assigned by environment

# ============ Create Agent ============
# State dimension: (view_size * view_size * 2) + global_features
state_dim = (2 * VIEW_THRESHOLD + 1) * (2 * VIEW_THRESHOLD + 1) * 2 + 2
action_dim = 8  # 8 directional movements

print(f"Creating DQN agent...")
print(f"  State dimension: {state_dim}")
print(f"  Action dimension: {action_dim}")

agent = DQAgent(
    state_dim=state_dim,
    action_dim=action_dim,
    lr=0.001,
    gamma=0.90,
    epsilon=1.0,
    epsilon_min=0.01,
    epsilon_decay=0.998,
    memory_size=20000,
    batch_size=32,
    target_update_freq=1000
)

# ============ Create Agents Dictionary ============
# same agent instance for all robots
agents = {f'agent{i+1}': agent for i in range(NUM_ROBOTS)}

# ============ Create Environment ============
print("Initializing environment...")
env = GoalChasingEnvironment(
    board=board,
    agents=agents,
    config={
        'board_size': BOARD_SIZE,
        'view_threshold': VIEW_THRESHOLD,
        'closeness_threshold': CLOSENESS_THRESHOLD,
        'num_robots': NUM_ROBOTS,
        'reset_on_goal': True  # Remove robots when they reach goals
    }
)

# ============ Create Runner ============
runner = GameRunner(env)

# ============ Optional: Custom Callbacks ============
def training_callback(board, agents:dict[str,DQAgent], step, epoch):
    """Called every step during training"""
    i = 0
    agents[f'agent{i+1}'].epsilon *= agents[f'agent{i+1}'].epsilon_decay
    agents[f'agent{i+1}'].epsilon = min(agents[f'agent{i+1}'].epsilon, agents[f'agent{i+1}'].epsilon_min)

    assert agents['agent1'].epsilon == agents['agent2'].epsilon, "different agent objects"

    if step % 10 == 0 and epoch % 2 == 0:
        info = env.get_info()
        print("")
        print(info)
        print("")
        # print(f"  Epoch {epoch}, Step {step}: {info['num_active_robots']} robots active")

def epoch_callback(board, agents, epoch, metrics):
    """Called after each epoch"""
    if epoch % 1 == 0:
        avg_reward = np.mean([r[f'agent{i+1}'] for r in metrics['rewards'][-10:] for i in range(NUM_ROBOTS)])
        episode_length = np.mean(metrics['episode_lengths'][-10:])
        print(f"Epoch {epoch}: Avg Reward = {avg_reward:.2f}, Avg Episode Length = {episode_length:.0f}")

# ============ Run Training ============
print("\nStarting training...")
print(f"  Epochs: {EPOCHS}")
print(f"  Max steps per episode: 1000")
print("-" * 60)

metrics = runner.run(
    epochs=EPOCHS,
    max_steps_per_episode=1000,
    reward_functions=None,  # Use default reward function
    termination_condition=None,  # Use default termination
    step_callback=training_callback,
    episode_callback=epoch_callback,
    render=False,
    render_last_epoch=True,
    save_metrics=False,
    save_models=False,
    save_directory='./saved_models/goal_chasing_basic',
    verbose=2
)

print("\n" + "=" * 60)
print("Training complete!")
print("=" * 60)
print(f"Total epochs: {len(metrics['episode_lengths'])}")
print(f"Average episode length: {np.mean(metrics['episode_lengths']):.2f}")
print(f"Final 10 epochs avg reward: {np.mean([r[f'agent{i+1}'] for r in metrics['rewards'][-10:] for i in range(NUM_ROBOTS)]):.2f}")