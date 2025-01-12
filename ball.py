import math

class Ball:
    def __init__(self, r=2, vel=1, dir=[0, 1]):
        self.x = 0.0  # Floating-point for precise tracking
        self.y = 0.0
        self.r = r
        self.vel = vel
        self.dir = dir

    def move(self, l_paddle, r_paddle, board):
        # Update floating-point position
        x = self.x + self.vel * self.dir[1]
        y = self.y + self.vel * self.dir[0]

        if self.dir[1] > 0:  # right paddle
            c1 = self.x < r_paddle.x                                    # old position is before paddle position
            c2 = r_paddle.y <= y <= r_paddle.y + r_paddle.length        # new position can hit the paddle
            c3 = x >= r_paddle.x                                       # new position is through paddle position
            if c1 and c3 and c2:                                       # Stick to the point to collision
                self.y = (self.dir[0] / self.dir[1]) * (r_paddle.x - self.x) + self.y
                self.x = r_paddle.x
                self.dir[1] = -self.dir[1]  # Reverse direction after hitting the paddle
                self.handle_paddle_collision(r_paddle)
            else:
                self.x = x
                self.y = y
        else:  # left paddle
            c1 = self.x > l_paddle.x                                    # old position is before paddle position
            c2 = l_paddle.y <= y <= l_paddle.y + l_paddle.length        # new position can hit the paddle
            c3 = x <= l_paddle.x                                       # new position is through paddle position
            if c1 and c3 and c2:                                       # Stick to the point to collision
                self.y = (self.dir[0] / self.dir[1]) * (l_paddle.x - self.x) + self.y
                self.x = l_paddle.x
                self.dir[1] = -self.dir[1]  # Reverse direction after hitting the paddle
                self.handle_paddle_collision(l_paddle)
            else:
                self.x = x
                self.y = y

        # Check for wall bounces
        if self.y <= 0:  # Top wall
            self.y = 0
            self.dir[0] = -self.dir[0]
        elif self.y >= board.size - 1:  # Bottom wall
            self.y = board.size - 1
            self.dir[0] = -self.dir[0]

        # Check for scoring
        if self.x <= 0:  # Right player scores
            board.increment_score(2)
            board.reset_ball(self)
        elif self.x >= board.size - 1:  # Left player scores
            board.increment_score(1)
            board.reset_ball(self)


    def handle_paddle_collision(self, paddle, transfer_factor=0.3):
        # Calculate the paddle's center
        paddle_center = paddle.y + paddle.length // 2

        # Calculate the vertical offset
        offset = self.y - paddle_center

        # Apply momentum transfer to vertical direction
        self.dir[0] += offset * transfer_factor

        # Normalize direction to maintain constant speed
        magnitude = math.sqrt(self.dir[0]**2 + self.dir[1]**2)
        self.dir[0] /= magnitude
        self.dir[1] /= magnitude
