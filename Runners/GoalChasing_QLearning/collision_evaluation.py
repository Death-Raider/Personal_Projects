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
from Runners.GoalChasing_QLearning.base import build_model

import numpy as np

def trivial_action(state):
    goal_dx = state[-2]
    goal_dy = state[-1]
    
    # Map (dx, dy) to closest direction
    # DIR: [NE, N, NW, W, E, SW, S, SE]
    
    # row: [-1, -1, -1,  0, 0,  1,  1,  1]  (dy)
    # col: [-1,  0,  1, -1, 1, -1,  0,  1]  (dx)
    
    angle = np.arctan2(-goal_dy, goal_dx)  # negative dy because row increases downward
    
    # Convert angle to 0-7 direction index
    # Angles for each direction:
    dir_angles = np.array([135, 90, 45, 180, 0, 225, 270, 315]) * np.pi / 180
    
    # Find closest direction
    angle = angle % (2 * np.pi)
    diffs = np.abs(dir_angles - angle)
    diffs = np.minimum(diffs, 2 * np.pi - diffs)  # handle wrap-around
    # print(int(np.argmin(diffs)))
    return int(np.argmin(diffs))

# Values
BOARD_SIZES = [50,60,70,80,90,100]
ROBOT_COUNTS = [5,10,15,20,25,30]
# Setup
state_dim = (2 * 10 + 1) ** 2 * 2 + 2
action_dim = 8

matrix_data = {
    'CADRL-Style': np.ones((6,6))*(-1),
    'DQN (Greedy)' : np.ones((6,6))*(-1)
}
for b,board_size in enumerate(BOARD_SIZES):
    for r,num_robots in enumerate(ROBOT_COUNTS):
        
        DQN_agent = DQAgent(state_dim, action_dim)
        DQN_agent.build_model = build_model
        DQN_agent.initlize_models()
        DQN_agent.load_model('results/DQN_(Greedy)_9/agent1_epoch_final')
        DQN_agent.epsilon = 0.05  # No exploration during evaluation
        DQN_agent.epsilon_min = 0.0
        DQN_agent.epsilon_decay = 0.0
        DQN_agent.batch_size = 1  # No training during evaluation
        
        CADRL_agent = CADRLStyleAgent(state_dim, action_dim, num_action_samples=8)
        CADRL_agent.build_model = build_model
        CADRL_agent.initlize_models()
        CADRL_agent.load_model('results/CADRL-Style_9/agent1_epoch_final')
        CADRL_agent.epsilon = 0.05  # No exploration during evaluation
        CADRL_agent.epsilon_min = 0.0
        CADRL_agent.epsilon_decay = 0.0
        CADRL_agent.batch_size = 1  # No training during evaluation
        
        agents_configs = {
            'CADRL-Style': CADRL_agent,
            'DQN (Greedy)': DQN_agent,
        }
        board_config = {
            'board_size': board_size,
            'view_threshold': 10,
            'closeness_threshold': 4,
            'num_robots': num_robots,
            'reset_on_goal': True  # Remove robot when goal reached
        }
        results = {}
        
        for name, agent in agents_configs.items():
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print('='*60)
            Collison_Data_Matrix = []
            # ============ Optional: Custom Callbacks ============
            def training_callback(board:Board, agents:dict[str,DQAgent], step:int, epoch:int, runner:GameRunner):
                """Called every step during training"""
                info = runner.env.get_info()
                # print(f"Step {step}, Epoch {epoch}:\n\t{info}\n")
                
                all_collisions = [info['robots'].get(e,{'collisions':0})['collisions'] for e in range(1,num_robots+1)]
                global Collison_Data_Matrix
            
                Collison_Data_Matrix.append(all_collisions)
            # Create fresh environment
            board = Board(size=board_size)
            board.max_players = num_robots
            agents = {}
            for i in range(num_robots):
                agents[f'agent{i+1}'] = agent
            
            env = GoalChasingEnvironment(board, agents, config=board_config)
            env.add_robots()
            runner = GameRunner(env)
            
            metrics = runner.run(
                epochs=5,
                max_steps_per_episode=200,
                reward_functions=None,  # Use default reward function
                termination_condition=None,  # Use default termination
                step_callback=training_callback,
                episode_callback=None,
                render=False,
                render_last_epoch=False,
                save_metrics=False,
                save_models=False,
                save_directory=f'results/{name.replace(" ", "_")}_eval_extra',
                verbose=2,
                train=False
            )
            results[name] = metrics
        
            Collison_Data_Matrix = np.array(Collison_Data_Matrix)
            total_collisions_agent_wise = np.sum(Collison_Data_Matrix, axis=0) # Agent wise collisions across all epochs
            total_collisions_step_wise = np.sum(Collison_Data_Matrix, axis=1) # step wise collisions across all agents
            total_collisions = np.sum(total_collisions_agent_wise) # Total collisions across all agents and epochs
            
            total_robot_steps = num_robots * len(Collison_Data_Matrix)
            matrix_data[name][r][b] = total_collisions / total_robot_steps
        
            print(f"Total Collisions for {name}:\nAgent Wise: {total_collisions_agent_wise}\nEpoch Wise: {total_collisions_step_wise}\nOverall: {total_collisions}\nTotal Steps: {total_robot_steps}")
            Collison_Data_Matrix = []