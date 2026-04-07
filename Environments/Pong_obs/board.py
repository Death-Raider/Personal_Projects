from Environments.Pong_obs.ball import Ball
from Environments.Pong_obs.paddle import Paddle
import random
import numpy as np


class Obstacle:
    """Axis-aligned rectangular obstacle. Collision is zone-based (x_start..x_end width)."""
    VALUE = 4  # board cell marker

    def __init__(self, x_start: int, x_end: int, y_start: int, y_end: int):
        self.x_start = x_start      # left edge (inclusive)
        self.x_end   = x_end        # right edge (inclusive)
        self.y_start = y_start
        self.y_end   = y_end        # exclusive

    def contains_y(self, y: float) -> bool:
        return self.y_start <= y < self.y_end


class Board:
    def __init__(self, size=100, paddle_length=10, paddle_pos=3,
                 obstacle_width=2):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.scores = {1: 0, 2: 0}
        self.ball = Ball(r=1, vel=1, dir=[0, 1])
        self.l_paddle = Paddle(length=paddle_length, x=paddle_pos, y=self.size // 2)
        self.r_paddle = Paddle(length=paddle_length, x=self.size - paddle_pos, y=self.size // 2)

        # Staggered obstacles at 1/3 and 2/3 of board width.
        # obs1 (left bar)  occupies the TOP half:    y = 0       .. mid - gap
        # obs2 (right bar) occupies the BOTTOM half: y = mid+gap .. size
        # Keeps the horizontal midline (ball spawn row) permanently clear.
        mid  = size // 2
        gap  = mid//2# max(1, int(size * 0.05))   # clear band around midline
        hw   = obstacle_width // 2

        self.obstacles: list[Obstacle] = [
            Obstacle(x_start=size // 3 - hw, x_end=size // 3 + hw,
                     y_start=0, y_end=mid - gap),
            Obstacle(x_start=2 * size // 3 - hw, x_end=2 * size // 3 + hw,
                     y_start=mid + gap, y_end=size),
        ]

    # ── board update ──────────────────────────────────────────────────────────

    def update(self):
        self.board = [[0] * self.size for _ in range(self.size)]

        for i in range(self.l_paddle.y, self.l_paddle.y + self.l_paddle.length):
            if 0 <= i < self.size:
                self.board[int(i)][self.l_paddle.x] = 1

        for i in range(self.r_paddle.y, self.r_paddle.y + self.r_paddle.length):
            if 0 <= i < self.size:
                self.board[int(i)][self.r_paddle.x] = 2

        bx, by = int(round(self.ball.x)), int(round(self.ball.y))
        if 0 <= bx < self.size and 0 <= by < self.size:
            self.board[by][bx] = 3

        for obs in self.obstacles:
            for col in range(obs.x_start, obs.x_end + 1):
                for row in range(obs.y_start, obs.y_end):
                    if 0 <= row < self.size and 0 <= col < self.size:
                        self.board[row][col] = Obstacle.VALUE

    # ── scoring / reset ───────────────────────────────────────────────────────

    def increment_score(self, player):
        if player in self.scores:
            self.scores[player] += 1

    def reset_ball(self):
        self.ball.x = self.size // 2
        self.ball.y = self.size // 2
        self.ball.dir = [0, random.choice([-1, 1])]
        self.ball.obstacle_crosses = [0] * len(self.obstacles)

    # ── state ─────────────────────────────────────────────────────────────────

    def current_board_state(self):
        """[y1, y2, by, bx, angle, obs1_cross, obs2_cross]
        obs_cross: 0=none, 1=L->R, -1=R->L"""
        ball_angle = np.arctan2(-self.ball.dir[0], self.ball.dir[1])
        if ball_angle < 0:
            ball_angle += 2 * np.pi
        crosses = getattr(self.ball, 'obstacle_crosses', [0] * len(self.obstacles))
        return ([self.l_paddle.y, self.r_paddle.y,
                 round(self.ball.y), round(self.ball.x),
                 round(ball_angle * 180 / np.pi)]
                + list(crosses))

    def set_state(self, state):
        y1, y2, by, bx, a = state[:5]
        self.l_paddle.y = int(y1)
        self.r_paddle.y = int(y2)
        self.ball.y = by
        self.ball.x = bx
        self.ball.dir = [-np.sin(a * np.pi / 180), np.cos(a * np.pi / 180)]

    def do_board_action(self, player=1, action=0):
        if action == 0:
            return
        if action == 1 and player == 1:
            self.l_paddle.move(direction=1, board_size=self.size)
        elif action == 2 and player == 1:
            self.l_paddle.move(direction=-1, board_size=self.size)
        elif action == 1 and player == 2:
            self.r_paddle.move(direction=1, board_size=self.size)
        elif action == 2 and player == 2:
            self.r_paddle.move(direction=-1, board_size=self.size)

    def get_board_score(self):
        return self.scores

    def reset_score(self):
        self.scores = {1: 0, 2: 0}