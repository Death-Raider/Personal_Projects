from ball import Ball
from paddle import Paddle
import keyboard

class Board:
    def __init__(self, size=100):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.scores = {1: 0, 2: 0}

    def update(self, l_paddle, r_paddle, ball):
        self.board = [[0] * self.size for _ in range(self.size)]

        # Draw left paddle
        for i in range(l_paddle.y, l_paddle.y + l_paddle.length):
            if 0 <= i < self.size:
                self.board[i][l_paddle.x] = 1

        # Draw right paddle
        for i in range(r_paddle.y, r_paddle.y + r_paddle.length):
            if 0 <= i < self.size:
                self.board[i][r_paddle.x] = 1

        # Draw the ball
        if 0 <= ball.x < self.size and 0 <= ball.y < self.size:
            self.board[ball.y][ball.x] = 3

    def increment_score(self, player):
        if player in self.scores:
            self.scores[player] += 1

    def reset_ball(self, ball):
        ball.x = self.size // 2
        ball.y = self.size // 2
        ball.dir = [0, 1] if ball.dir[1] > 0 else [0, -1]

    def pong_game(self):
        ball = Ball(r=2, vel=1, dir=[0, 1])
        l_paddle = Paddle(length=5, x=10, y=self.size // 2)
        r_paddle = Paddle(length=5, x=self.size - 10, y=self.size // 2)
        ball.x, ball.y = self.size // 2, self.size // 2

        while True:
            self.update(l_paddle, r_paddle, ball)
            yield self.board, self.scores

            ball.move(l_paddle, r_paddle, self)

            if keyboard.is_pressed('e'):
                l_paddle.move(direction=-1, board_size=self.size)
            elif keyboard.is_pressed('d'):
                l_paddle.move(direction=1, board_size=self.size)

            if keyboard.is_pressed('up'):
                r_paddle.move(direction=-1, board_size=self.size)
            elif keyboard.is_pressed('down'):
                r_paddle.move(direction=1, board_size=self.size)