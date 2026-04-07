"""
Pong Environment wrapper for MARL framework
"""

import numpy as np
from typing import Dict, Any, Callable
from Environments.baseenvironment import BaseEnvironment
from Environments.Pong.board import Board
import matplotlib.pyplot as plt

class PongEnvironment(BaseEnvironment):
    """
    Pong environment for 2-player competitive game
    
    State: [paddle1_y, paddle2_y, ball_y, ball_x, ball_angle]
    Actions: [0=idle, 1=up, 2=down]
    """
    
    def __init__(self, 
                 board: Board, 
                 agents: Dict[str, Any],
                 config: Dict[str, Any] = None):
        """
        Initialize Pong environment
        
        Args:
            board: Pong board instance
            agents: Dictionary of agents (should have 2 agents)
            config: Optional configuration dictionary
        """
        super().__init__(board, agents)
        
        # Default config
        self.config = {
            'board_size': 40,
            'paddle_length': 10,
            'max_score': 21,
            'state_encoding': 'discrete'  # or 'continuous'
        }
        if config:
            self.config.update(config)
        
        # For discrete state encoding (Q-Learning)
        self.base_y1 = self.config['board_size'] - self.config['paddle_length'] + 1
        self.base_y2 = self.config['board_size'] - self.config['paddle_length'] + 1
        self.base_bx = self.config['board_size'] + 1
        self.base_by = self.config['board_size'] + 1
        self.base_a = 360
        
        self.n_states = self.base_y1 * self.base_y2 * self.base_bx * self.base_by * self.base_a
    
    # ============ Required Implementations ============
    
    def reset_episode(self) -> None:
        """Reset for new Pong episode"""
        self.board.reset_score()
        self.board.reset_ball()
        self.current_step = 0
    
    def get_states(self) -> Dict[str, Any]:
        """
        Get current state for both players
        
        Returns:
            Dict with state for each agent (both see same state in Pong)
        """
        # Get raw state from board
        raw_state = self.board.current_board_state()
        
        # Encode state based on configuration
        if self.config['state_encoding'] == 'discrete':
            state = self.state_to_index(*raw_state)
        else:
            state = raw_state
        
        # Both agents see the same global state in Pong
        return {name: state for name in self.agents.keys()}
    
    def execute_actions(self, actions: Dict[str, int]) -> None:
        """
        Execute paddle movements and ball physics
        
        Args:
            actions: Dict mapping agent names to actions (0=idle, 1=up, 2=down)
        """
        # Execute paddle actions
        for agent_name, action in actions.items():
            player = self._get_player_number(agent_name)
            self.board.do_board_action(player=player, action=action)
        
        # Move ball
        self.board.ball.move(self.board.l_paddle, self.board.r_paddle, self.board)
        
        # Update board visualization
        self.board.update()
        
        self.current_step += 1
    
    def get_default_reward_function(self) -> Callable:
        """
        Default Pong reward: score difference + paddle alignment
        
        Returns:
            Reward function
        """
        def pong_reward(board, agent_name, **kwargs):
            score = board.get_board_score()
            player = self._get_player_number(agent_name)
            paddle = board.l_paddle if player == 1 else board.r_paddle
            ball = board.ball
            
            # Score-based reward
            if player == 1:
                reward = 0.1 * (score[1] - score[2])
            else:
                reward = 0.1 * (score[2] - score[1])
            
            # Paddle alignment reward
            paddle_center = paddle.y + paddle.length // 2
            alignment_bonus = 2 if abs(ball.y - paddle_center) < paddle.length // 2 else -2
            reward += alignment_bonus
            
            # Coverage reward (is ball within paddle range?)
            coverage_bonus = 2 if paddle.y < ball.y < paddle.y + paddle.length else -2
            reward += coverage_bonus
            
            return reward
        
        return pong_reward
    
    def get_default_termination_condition(self) -> Callable:
        """
        Default termination: game ends when total score reaches max_score
        
        Returns:
            Termination condition function
        """
        def pong_termination(board, step, **kwargs):
            score = board.get_board_score()
            return (score[1] + score[2]) >= self.config['max_score']
        
        return pong_termination
    
    # ============ Optional Overrides ============
    
    def check_done(self, step: int) -> Dict[str, bool]:
        """Both players done at same time in Pong"""
        termination_fn = self.get_default_termination_condition()
        is_done = termination_fn(self.board, step)
        return {name: is_done for name in self.agents.keys()}
    
    def get_info(self) -> Dict[str, Any]:
        """Additional info about game state"""
        score = self.board.get_board_score()
        return {
            'score': score,
            'ball_position': (self.board.ball.x, self.board.ball.y),
            'ball_direction': self.board.ball.dir,
            'step': self.current_step
        }
    def render_init(self, runner):
        self.fig = plt.figure(figsize=(8, 6))
        
        # Main board plot (left, large)
        self.ax_board = self.fig.add_subplot(2, 3, (1, 4))  # spans rows 1-2, col 1
        
        # Smaller plots on the right
        self.ax_r1 = self.fig.add_subplot(2, 3, 2)  # Player 1 Reward
        self.ax_l1 = self.fig.add_subplot(2, 3, 3)  # Player 1 Loss
        self.ax_r2 = self.fig.add_subplot(2, 3, 5)  # Player 2 Reward
        self.ax_l2 = self.fig.add_subplot(2, 3, 6)  # Player 2 Loss

        self.fig.tight_layout(pad=2.0)

        # History buffers
        self.history = {
            'r1': [], 'l1': [],
            'r2': [], 'l2': [],
        }

    def render(self, runner):
        # --- Board ---
        self.ax_board.clear()
        self.ax_board.imshow(self.board.board, cmap='gray')
        self.ax_board.set_title(
            f'Step: {self.current_step} | Score: {self.board.get_board_score()}',
            fontsize=12, fontweight='bold'
        )
        self.ax_board.axis('off')

        # Append new values if provided
        reward1 = runner.epoch_rewards['agent1'][-1] if 'agent1' in runner.epoch_rewards else None
        loss1 = runner.epoch_losses['agent1'][-1] if 'agent1' in runner.epoch_losses else None
        reward2 = runner.epoch_rewards['agent2'][-1] if 'agent2' in runner.epoch_rewards else None
        loss2 = runner.epoch_losses['agent2'][-1] if 'agent2' in runner.epoch_losses else None

        for key, val in zip(['r1', 'l1', 'r2', 'l2'], [reward1, loss1, reward2, loss2]):
            if val is not None:
                self.history[key].append(val)
                self.history[key] = self.history[key][-500:]

        # --- Helper to plot a metric ---
        def plot_metric(ax, data, title, color):
            ax.clear()
            ax.plot(data, color=color, linewidth=1.2)
            ax.set_title(title, fontsize=9)
            ax.set_xlabel('Step', fontsize=7)
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.3)
            if data:
                ax.set_ylim(min(data) - abs(min(data)) * 0.1 - 1e-6,
                            max(data) + abs(max(data)) * 0.1 + 1e-6)

        plot_metric(self.ax_r1, self.history['r1'], 'Player 1 — Reward', 'steelblue')
        plot_metric(self.ax_l1, self.history['l1'], 'Player 1 — Loss',   'tomato')
        plot_metric(self.ax_r2, self.history['r2'], 'Player 2 — Reward', 'mediumseagreen')
        plot_metric(self.ax_l2, self.history['l2'], 'Player 2 — Loss',   'orange')

        self.fig.tight_layout(pad=2.0)
        plt.pause(0.001)
    # ============ State Encoding for Discrete Spaces ============
    
    def state_to_index(self, y1, y2, bx, by, a) -> int:
        """Convert state tuple to single index (for Q-Learning)"""
        y_size = self.config['board_size'] - self.config['paddle_length'] + 1
        a = a%360
        
        if not (0 <= y1 < y_size):
            raise ValueError(f"y1 out of range: {y1} (should be 0 to {y_size-1})")
        if not (0 <= y2 < y_size):
            raise ValueError(f"y2 out of range: {y2}")
        if not (0 <= bx <= self.config['board_size']):
            raise ValueError(f"bx out of range: {bx}")
        if not (0 <= by <= self.config['board_size']):
            raise ValueError(f"by out of range: {by}")
        if not (0 <= a < 360):
            raise ValueError(f"angle out of range: {a} (should be 0-359)")
        return (y1 
                + y2 * self.base_y1 
                + bx * self.base_y1 * self.base_y2 
                + by * self.base_y1 * self.base_y2 * self.base_bx 
                + a * self.base_y1 * self.base_y2 * self.base_bx * self.base_by)
    
    def index_to_state(self, index: int) -> tuple:
        """Convert index back to state tuple"""
        y1 = index % self.base_y1
        y2 = (index // self.base_y1) % self.base_y2
        bx = (index // (self.base_y1 * self.base_y2)) % self.base_bx
        by = (index // (self.base_y1 * self.base_y2 * self.base_bx)) % self.base_by
        a = index // (self.base_y1 * self.base_y2 * self.base_bx * self.base_by)
        return (y1, y2, bx, by, a)
    
    # ============ Helper Methods ============
    
    def _get_player_number(self, agent_name: str) -> int:
        """Map agent name to player number (1 or 2)"""
        if 'agent1' in agent_name.lower() or 'left' in agent_name.lower() or 'player1' in agent_name.lower():
            return 1
        else:
            return 2