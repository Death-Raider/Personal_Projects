import math

class Ball:
    def __init__(self, r=2, vel=1, dir=[0, 1]):
        self.x = 0
        self.y = 0
        self.r = r
        self.dir = dir

    def move(self, l_paddle, r_paddle, board):
        x = math.ceil(self.x + self.dir[1])
        y = math.ceil(self.y + self.dir[0])

        if self.dir[1] > 0:  # right paddle
            c1 = self.x < r_paddle.x                                    # old position is before paddle position
            c2 = r_paddle.y <= y <= r_paddle.y + r_paddle.length        # new position can hit the paddle
            c3 = x >= r_paddle.x                                       # new position is through paddle position
            if c1 and c3 and c2:                                       # Stick to the point to collision
                self.y = int((self.dir[0] / self.dir[1]) * (r_paddle.x - self.x) + self.y)
                self.x = r_paddle.x
                self.dir[1] = -self.dir[1]  # Reverse direction after hitting the paddle
            else:
                self.x = x
                self.y = y
        else:  # left paddle
            c1 = self.x > l_paddle.x                                    # old position is before paddle position
            c2 = l_paddle.y <= y <= l_paddle.y + l_paddle.length        # new position can hit the paddle
            c3 = x <= l_paddle.x                                       # new position is through paddle position
            if c1 and c3 and c2:                                       # Stick to the point to collision
                self.y = int((self.dir[0] / self.dir[1]) * (l_paddle.x - self.x) + self.y)
                self.x = l_paddle.x
                self.dir[1] = -self.dir[1]  # Reverse direction after hitting the paddle
            else:
                self.x = x
                self.y = y

        # Check for wall bounces
        if y <= 0:  # Top wall
            self.y = 0
            self.dir[0] = -self.dir[0]  # Reverse vertical direction
        elif y >= board.size - 1:  # Bottom wall
            self.y = board.size - 1
            self.dir[0] = -self.dir[0]  # Reverse vertical direction

        # Check for scoring
        if self.x <= 0:  # Right player scores
            board.increment_score(2)
            board.reset_ball(self)
        elif self.x >= board.size - 1:  # Left player scores
            board.increment_score(1)
            board.reset_ball(self)