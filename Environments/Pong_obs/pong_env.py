"""
Pong Environment wrapper for MARL framework
"""

import numpy as np
from typing import Dict, Any, Callable
from Environments.baseenvironment import BaseEnvironment
from Environments.Pong_obs.board import Board

import matplotlib.pyplot as plt

class PongEnvironment(BaseEnvironment):
    """
    Pong environment for 2-player competitive game.

    State: [paddle1_y, paddle2_y, ball_y, ball_x, ball_angle,
            obs1_cross, obs2_cross]
    Actions: [0=idle, 1=up, 2=down]

    Reward is strictly zero-sum: every reward given to one player is
    subtracted from the other, so no free rewards accumulate.
    """

    def __init__(self, board: Board, agents: Dict[str, Any],
                 config: Dict[str, Any] = None):
        super().__init__(board, agents)

        self.config = {
            'board_size': 40,
            'paddle_length': 10,
            'max_score': 21,
            'state_encoding': 'discrete',
            # Zero-sum reward weights
            'score_reward': 1.0,       # per point scored
            'alignment_reward': 3.0,    # paddle aligned with ball
            'obstacle_cross_reward': 1.0,  # ball cleared obstacle toward opponent
        }
        if config:
            self.config.update(config)

        if self.config['state_encoding'] == 'discrete':
            self.base_y1 = self.config['board_size'] - self.config['paddle_length'] + 1
            self.base_y2 = self.config['board_size'] - self.config['paddle_length'] + 1
            self.base_bx = self.config['board_size'] + 1
            self.base_by = self.config['board_size'] + 1
            self.base_a  = 360
            self.n_states = (self.base_y1 * self.base_y2 *
                            self.base_bx * self.base_by * self.base_a)
        else:
            self.n_states = 5 + len(self.board.obstacles)  # raw state size
    # ── required implementations ──────────────────────────────────────────────

    def reset_episode(self) -> None:
        self.board.reset_score()
        self.board.reset_ball()
        self.current_step = 0

    def get_states(self) -> Dict[str, Any]:
        raw = self.board.current_board_state()
        if self.config['state_encoding'] == 'discrete':
            # Discrete index uses only first 5 elements (no obstacle state)
            state = self.state_to_index(*raw[:5])
        else:
            state = raw
        return {name: state for name in self.agents.keys()}

    def execute_actions(self, actions: Dict[str, int]) -> None:
        for agent_name, action in actions.items():
            player = self._get_player_number(agent_name)
            self.board.do_board_action(player=player, action=action)

        self.board.ball.move(self.board.l_paddle, self.board.r_paddle, self.board)
        self.board.update()
        self.current_step += 1

    def get_default_reward_function(self) -> Callable:
        """
        Strictly zero-sum reward.

        Components (always mirrored: +R for p1 → −R for p2):
          • Score events  : ±score_reward
          • Paddle alignment with ball: ±alignment_reward
          • Obstacle crossing toward opponent: ±obstacle_cross_reward
            - ball crosses obs L→R  → favour player 1 (they pushed it through)
            - ball crosses obs R→L  → favour player 2
        """
        w_score   = self.config['score_reward']
        w_align   = self.config['alignment_reward']
        w_obs     = self.config['obstacle_cross_reward']

        def _zero_sum_reward(board, agent_name, **kwargs):
            player = self._get_player_number(agent_name)
            sign   = 1 if player == 1 else -1          # +1 for p1, -1 for p2

            score   = board.get_board_score()
            ball    = board.ball
            paddle  = board.l_paddle if player == 1 else board.r_paddle

            reward = 0.0

            # ── 1. Score delta (zero-sum) ─────────────────────────────────────
            score_delta = score[1] - score[2]
            reward += sign * w_score * score_delta

            # ── 2. Continuous alignment using distance + ball angle ───────────
            paddle_center = paddle.y + paddle.length / 2.0
            dy = ball.y - paddle_center                     # signed vertical difference

            # Horizontal distance (positive when ball is approaching your side)
            if player == 1:                                 # left paddle
                dx = ball.x - (paddle.x + 1)     # distance from right edge of paddle
            else:                                           # right paddle
                dx = paddle.x - ball.x                      # distance from left edge of paddle

            # Only apply shaping when ball is coming toward this player
            # Using angle: 0° = right, 90° = down, 180° = left, 270° = up (standard math angles)
            ball_angle = getattr(ball, 'angle', 0) % 360

            if player == 1:
                ball_coming_toward_me = 0 <= ball_angle < 180     # moving right-ish (vx > 0)
            else:
                ball_coming_toward_me = 180 <= ball_angle < 360   # moving left-ish (vx < 0)

            if ball_coming_toward_me and dx > 0:
                # Vertical alignment factor (1.0 = perfect, 0.0 = at edge or beyond)
                half_paddle = paddle.length / 2.0
                vertical_factor = max(0.0, 1.0 - abs(dy) / half_paddle)

                # Angle factor: how horizontal the ball is moving
                # Closer to 0° or 180° → more horizontal → easier to return accurately
                angle_from_horizontal = min(abs(ball_angle % 360), abs((ball_angle % 360) - 180))
                angle_factor = max(0.0, 1.0 - (angle_from_horizontal / 90.0))   # 0°/180° = 1.0, 90° = 0.0

                # Combine both
                alignment_factor = vertical_factor * (angle_factor ** 1.5)   # slight emphasis on good angle

                # Proximity weight: stronger reward when ball is closer
                max_dx = board.size * 0.85                     # adjust based on your board size
                proximity_factor = max(0.0, 1.0 - (dx / max_dx))

                reward += sign * w_align * alignment_factor * proximity_factor

            # ── 3. Obstacle crossing bonuses ───────────────────────────────────
            for cross in getattr(ball, 'obstacle_crosses', []):
                if cross != 0:
                    reward += sign * cross * w_obs

            return reward

        return _zero_sum_reward

    def get_default_termination_condition(self) -> Callable:
        def pong_termination(board, step, **kwargs):
            score = board.get_board_score()
            return (score[1] + score[2]) >= self.config['max_score']
        return pong_termination

    # ── optional overrides ────────────────────────────────────────────────────

    def check_done(self, step: int) -> Dict[str, bool]:
        is_done = self.get_default_termination_condition()(self.board, step)
        return {name: is_done for name in self.agents.keys()}

    def get_info(self) -> Dict[str, Any]:
        score = self.board.get_board_score()
        crosses = getattr(self.board.ball, 'obstacle_crosses', [])
        return {
            'score': score,
            'ball_position': (self.board.ball.x, self.board.ball.y),
            'ball_direction': self.board.ball.dir,
            'obstacle_crosses': crosses,
            'step': self.current_step,
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

    # ── state encoding ────────────────────────────────────────────────────────

    def state_to_index(self, y1, y2, bx, by, a) -> int:
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
                + a  * self.base_y1 * self.base_y2 * self.base_bx * self.base_by)

    def index_to_state(self, index: int) -> tuple:
        y1 = index % self.base_y1
        y2 = (index // self.base_y1) % self.base_y2
        bx = (index // (self.base_y1 * self.base_y2)) % self.base_bx
        by = (index // (self.base_y1 * self.base_y2 * self.base_bx)) % self.base_by
        a  = index // (self.base_y1 * self.base_y2 * self.base_bx * self.base_by)
        return (y1, y2, bx, by, a)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_player_number(self, agent_name: str) -> int:
        if any(k in agent_name.lower() for k in ('agent1', 'left', 'player1')):
            return 1
        return 2