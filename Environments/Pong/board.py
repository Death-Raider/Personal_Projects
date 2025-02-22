from Environments.Pong.ball import Ball
from Environments.Pong.paddle import Paddle
import random
import numpy as np

class Board:
    def __init__(self, size=100, paddle_length = 10, paddle_pos = 3):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.scores = {1: 0, 2: 0}
        self.ball = Ball(r=1, vel=1, dir=[0, 1])
        self.l_paddle = Paddle(length=paddle_length, x=paddle_pos, y=self.size // 2)
        self.r_paddle = Paddle(length=paddle_length, x=self.size - paddle_pos, y=self.size // 2)

    def update(self):
        self.board = [[0] * self.size for _ in range(self.size)]

        # Draw left paddle
        for i in range(self.l_paddle.y, self.l_paddle.y + self.l_paddle.length):
            if 0 <= i < self.size:
                self.board[int(i)][self.l_paddle.x] = 1

        # Draw right paddle
        for i in range(self.r_paddle.y, self.r_paddle.y + self.r_paddle.length):
            if 0 <= i < self.size:
                self.board[int(i)][self.r_paddle.x] = 2

        # Draw the ball (rounding position for display)
        ball_x = int(round(self.ball.x))
        ball_y = int(round(self.ball.y))
        if 0 <= ball_x < self.size and 0 <= ball_y < self.size:
            self.board[ball_y][ball_x] = 3

    def increment_score(self, player):
        if player in self.scores:
            self.scores[player] += 1

    def reset_ball(self):
        self.ball.x = self.size // 2
        self.ball.y = self.size // 2
        self.ball.dir = [0,random.choice([-1,1])] # [random.randrange(-1,1)+0.1, random.randrange(-1,1)+0.3]
        # mag = np.hypot(*self.ball.dir)
        # self.ball.dir[0] /= mag
        # self.ball.dir[1] /= mag

    def current_board_state(self):
        paddle_positions = [self.l_paddle.y, self.r_paddle.y]
        ball_position = [round(self.ball.y), round(self.ball.x)]
        ball_angle = np.arctan2(-self.ball.dir[0], self.ball.dir[1])
        if ball_angle < 0:
            ball_angle += 2*np.pi
        return paddle_positions + ball_position + [round(ball_angle*180/np.pi)]
    
    def set_state(self, state):
        y1,y2,by,bx,a = state
        self.l_paddle.y = int(y1)
        self.r_paddle.y = int(y2)
        self.ball.y = by
        self.ball.x = bx
        self.ball.dir = [-np.sin(a*np.pi/180), np.cos(a*np.pi/180)]
        
    def do_board_action(self,player=1,action=0):
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
        self.scores = {1:0, 2:0}