# Environments/GoalChasing/goal_chasing_environment.py
"""
Goal Chasing Environment wrapper for MARL framework
"""

import numpy as np
from typing import Dict, Any, Callable
from Environments.baseenvironment import BaseEnvironment
from Environments.GoalChasing.board import Board
from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib import cm

class GoalChasingEnvironment(BaseEnvironment):
    """
    Multi-agent goal chasing environment
    Robots navigate to goals while avoiding collisions
    
    State: Per-robot observation (local view + goal direction)
    Actions: 8 directional movements
    """
    
    def __init__(self,
                 board: Board,
                 agents: Dict[str, Any],
                 config: Dict[str, Any] = None):
        """
        Initialize Goal Chasing environment
        
        Args:
            board: Goal chasing board instance
            agents: Dictionary of agents
            config: Optional configuration
        """
        super().__init__(board, agents)
        
        # Default config
        self.config = {
            'board_size': 100,
            'view_threshold': 10,
            'closeness_threshold': 3,
            'num_robots': len(agents),
            'reset_on_goal': True  # Remove robot when goal reached
        }
        if config:
            self.config.update(config)
        
        self.board.max_players = self.config['num_robots']
    
    # ============ Required Implementations ============

    def add_robots(self):
        robots_and_goals = []
        for i in range(self.board.max_players):
            # Create robot
            robot = Robot(
                id=i + 1,
                h=1,
                w=1,
                closeness_threshold=self.config['closeness_threshold'],
                view_threshold=self.config['view_threshold']
            )
            
            # Create goal
            goal = Goal(id=i + 1)
            
            # Random initialization
            robot.set_random_init_state(self.board.size, self.board.size)
            robot.v = 1
            goal.set_random_goal(self.board.size, self.board.size)
            
            # Ensure goal is far from robot
            while robot.get_dist(goal)[0] < self.board.size * 0.5:
                goal.set_random_goal(self.board.size, self.board.size)
            
            robots_and_goals.append((robot, goal))

        # Add robots to board
        self.board.players = []
        for robot, goal in robots_and_goals:
            self.board.add_robot(robot, goal, None)  # Agent will be assigned by environment
    
    def reset_episode(self) -> None:
        """Reset all robots and goals to random positions"""
        self.add_robots()
        
        for robot, goal, agent in self.board.players:
            robot.set_random_init_state(self.config['board_size'], 
                                       self.config['board_size'])
            robot.v = 1
            goal.set_random_goal(self.config['board_size'], 
                               self.config['board_size'])
            
            # Ensure goal is far enough from robot
            while robot.get_dist(goal)[0] < self.config['board_size'] * 0.5:
                goal.set_random_goal(self.config['board_size'], 
                                   self.config['board_size'])
        
        # Update board state
        self._update_board()
        self.current_step = 0
    
    def get_states(self) -> Dict[str, Any]:
        """
        Get state observation for each robot
        Each robot has its own local view
        
        Returns:
            Dict mapping agent names to their observations
        """
        states = {}
        
        if not hasattr(self.board, 'players'):
            return states
        
        for robot, goal, agent in self.board.players:
            # Detect other robots in view
            robot.detect_robots()
            
            # Update references to detected robots
            for j in range(len(robot.detected_robots['id'])):
                robot.detected_robots["robot"][j] = self._get_robot_by_id(
                    robot.detected_robots['id'][j]
                )
            
            # Get state representation
            state = robot.get_DQL_state(goal)
            
            # Map to agent name
            agent_name = f'agent{robot.id}'
            if agent_name not in self.agents:
                agent_name = list(self.agents.keys())[0]  # Fallback for shared agent
            
            states[agent_name] = state
        
        return states
    
    def execute_actions(self, actions: Dict[str, int]) -> None:
        """
        Execute movement actions for all robots
        
        Args:
            actions: Dict mapping agent names to direction indices (0-7)
        """
        if not hasattr(self.board, 'players'):
            return
        
        # Set directions
        for robot, goal, agent in self.board.players:
            agent_name = f'agent{robot.id}'
            if agent_name not in actions:
                agent_name = list(self.agents.keys())[0]
            
            if agent_name in actions:
                robot._set_dir(actions[agent_name])
        
        # Execute movements
        for robot, goal, agent in self.board.players:
            robot.move(x_max=self.config['board_size'], 
                      y_max=self.config['board_size'])
        
        # Update board
        self._update_board()
        self.current_step += 1
    
    def get_default_reward_function(self) -> Callable:
        """
        Default Goal Chasing reward: distance to goal + collision avoidance
        
        Returns:
            Reward function
        """
        def goal_chasing_reward(board, agent_name, states=None, **kwargs):
            # Extract robot ID from agent name
            robot_id = int(agent_name.replace('agent', '')) if 'agent' in agent_name else 1
            
            # Find corresponding robot and goal
            robot, goal = None, None
            if hasattr(board, 'players'):
                for r, g, a in board.players:
                    if r.id == robot_id:
                        robot, goal = r, g
                        break
            
            if robot is None or goal is None:
                return 0.0
            
            # Calculate reward components
            distance = robot.get_dist(goal)[0]
            angle_dir = robot.DIR_ANGLES[robot.dir] * np.pi / 180
            angle_error = abs(robot.get_dist(goal)[1] - angle_dir) % (2 * np.pi)
            
            # Distance-based reward
            reward = 2 * (1 / (distance + 0.1))
            
            # Goal achievement bonus
            reward += 4 if distance < 1.3 else 0
            
            # Direction alignment reward
            reward += 5 * np.cos(angle_error / 2) ** 2
            
            # Time penalty (encourage efficiency)
            reward -= self.current_step * 0.01
            
            # Collision penalties
            collision_count = robot.check_collisions()
            if collision_count > 0:
                reward -= 10 * collision_count
            
            # Proximity-based collision avoidance
            for i, other_robot in enumerate(robot.detected_robots['robot']):
                if other_robot is None:
                    continue
                dist = robot.detected_robots['pos'][i][0]
                
                # Penalty for being too close
                if dist < robot.closeness_threshold:
                    reward -= 1.5 * (1 - dist / robot.closeness_threshold) ** 2
                
                # Bonus for maintaining safe distance
                if dist > robot.closeness_threshold * 1.5:
                    reward += 0.2
            
            return reward
        
        return goal_chasing_reward
    
    def get_default_termination_condition(self) -> Callable:
        """
        Default termination: all robots reached goals (removed from board)
        
        Returns:
            Termination condition function
        """
        def goal_chasing_termination(board, step, **kwargs):
            if not hasattr(board, 'players'):
                return True
            return len(board.players) == 0
        
        return goal_chasing_termination
    
    # ============ Optional Overrides ============
    
    def check_done(self, step: int) -> Dict[str, bool]:
        """Check if each robot has reached its goal"""
        dones = {}
        
        if hasattr(self.board, 'players'):
            for robot, goal, agent in self.board.players:
                agent_name = f'agent{robot.id}'
                if agent_name not in self.agents:
                    agent_name = list(self.agents.keys())[0]
                
                # Robot is done when it reaches goal
                dones[agent_name] = robot.get_dist(goal)[0] < 1.2
                
                # Remove robot from board if configured
                if dones[agent_name] and self.config['reset_on_goal']:
                    self.board.update_robots()
        
        return dones
    
    def get_info(self) -> Dict[str, Any]:
        """Additional info about environment state"""
        info = {
            'num_active_robots': len(self.board.players) if hasattr(self.board, 'players') else 0,
            'step': self.current_step
        }
        
        # Per-robot info
        if hasattr(self.board, 'players'):
            info['robots'] = {}
            for robot, goal, agent in self.board.players:
                info['robots'][robot.id] = {
                    'position': (robot.x, robot.y),
                    'goal_distance': robot.get_dist(goal)[0],
                    'collisions': robot.check_collisions()
                }
        
        return info
    
    def render_init(self)->None:
        def create_figure(robot_count):
            """
                create the template figure and returns the proper axis for all the robots and the board.
                first column and first two rows are for the board. Rest are for robots
                
                Returns figure, board axis, list of robot axis
            """

            total_boxes = robot_count + 2 # plus two for the main board rowspan
            row_count = max(2, int(np.ceil(np.sqrt(total_boxes / 1.5))))
            col_count = max(1, int(np.ceil(total_boxes / row_count)))

            print(f"Grid size = {row_count} rows x {col_count} cols")
            
            main_fig = plt.figure(figsize=(20,20))
            gs = gridspec.GridSpec(row_count,col_count,
                                figure=main_fig,
                                wspace=0.2,   # horizontal space between subplots
                                    hspace=0.6)    # vertical space between subplots
            
            ax1 = main_fig.add_subplot(gs[:2,0]) # main images
            axs = []
            for i in range(row_count):
                for j in range(col_count):
                    if (i in (0,1)) and (j == 0): # reserved for the board axis
                        continue
                    ax = main_fig.add_subplot(gs[i, j])
                    axs.append(ax)
            return main_fig, ax1, axs
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        plt.ion()
        self.render_fig, self.render_ax1, self.render_axs = create_figure(self.board.max_players)

    def render(self)->None:
        
        def game_plotting(board, ax1, axs, robot_count):
            
            cmap = cm.get_cmap('viridis').copy()
            cmap.set_bad(color="#E6E6E6")

            for [r,g,a] in board.players:
                # masked = np.ma.masked_where(r.view==0, r.view)
                masked = np.ma.masked_array(r.view, mask=np.ones_like(r.view, dtype=bool))
                axs[r.id-1].imshow(masked, cmap=cmap, vmin=-robot_count, vmax=robot_count)
                # axs[r.id-1].set_title(f"{r.id}\n"+','.join(map(str,r.detected_robots['id'])))
                axs[r.id-1].set_title(f"{r.id}\n"+r.check_collisions()*"X")
                view_h, view_w = r.view.shape
                center_x, center_y = (view_w-1) / 2, (view_h-1) / 2

                # Closeness threshold circle in robot view
                circle_view = patches.Circle(
                    (center_x, center_y),
                    radius=r.closeness_threshold,
                    fill=False,
                    color='red',
                    linewidth=0.5,
                )
                axs[r.id-1].add_patch(circle_view)

                axs[r.id-1].text(center_x, center_y, f"{r.id}🤖", fontsize=12, ha='center', va='center', color="#071068") # add robot icon in view
                for other_r in r.detected_robots['robot']: # add robot icon of detected robots in view
                    if other_r is None:
                        continue
                    other_index = r.detected_robots['id'].index(other_r.id)
                    other_pos = r.detected_robots['pos'][other_index]
                    other_x = center_x + other_pos[0] * np.cos(other_pos[1])
                    other_y = center_y - other_pos[0] * np.sin(other_pos[1])
                    axs[r.id-1].text(other_x, other_y, f"{other_r.id}🤖", fontsize=10, ha='center', va='center', color="#071068") # add other robot icon in view
                
                # add other goal icon in view
                goal_indicies = np.where(r.view < 0)
                for gy,gx in zip(goal_indicies[0], goal_indicies[1]):
                    goal_x = gx
                    goal_y = gy
                    axs[r.id-1].text(goal_x, goal_y, f"{-int(r.view[goal_y, goal_x])}⭐", fontsize=10, ha='center', va='center', color='#DAA520') # add goal icon in view

                # Collision threshold circle in robot view
                collision_view = patches.Circle(
                    (center_x, center_y),
                    radius=r.closeness_threshold*0.5,
                    fill=False,
                    color='black',
                    linewidth=0.5,
                )
                axs[r.id-1].add_patch(collision_view)

                circle_board = patches.Circle(
                    (r.x + (r.w-1) / 2, r.y + (r.h-1) / 2),
                    radius=r.closeness_threshold,
                    fill=False,
                    color='red',
                    linewidth=0.5,
                )
                ax1.add_patch(circle_board)
                robot_x, robot_y = r.x, r.y
                goal_x, goal_y = g.x, g.y
                ax1.text(robot_x, robot_y, f"{r.id}🤖", fontsize=12, ha='center', va='center', color="#071068") # add robot icon in board
                ax1.text(goal_x, goal_y, f"{g.id}⭐", fontsize=12, ha='center', va='center', color='#DAA520') # add goal icon in board

            # masked_board = np.ma.masked_where(board.board == 0, board.board)
            masked_board = np.ma.masked_array(board.board, mask=np.ones_like(board.board, dtype=bool))
            ax1.imshow(masked_board, cmap=cmap, vmin=-robot_count, vmax=robot_count)
            plt.pause(0.01)
            for [r,g,a] in board.players:
                axs[r.id-1].cla()
            ax1.cla()

        game_plotting(self.board, self.render_ax1, self.render_axs, self.board.max_players)
    
    # ============ Helper Methods ============
    
    def _update_board(self):
        """Update board visualization and state"""
        self.board.update_robots()
        self.board.draw_board()
        self.board.update_views()
    
    def _get_robot_by_id(self, robot_id: int):
        """Get robot instance by ID"""
        if hasattr(self.board, 'players'):
            for r, g, a in self.board.players:
                if r.id == robot_id:
                    return r
        return None