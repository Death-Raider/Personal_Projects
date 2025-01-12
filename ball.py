import math

class Ball:
    def __init__(self, r=2, vel=1, dir=[0, 1]):
        self.x = 0
        self.y = 0
        self.r = r
        self.dir = dir

    def move(self, l_paddle, r_paddle, board_size):
        x = math.ceil(self.x + self.dir[1])
        y = math.ceil(self.y + self.dir[0])

        # if between old and new position there is a paddle, then teleport the ball to the paddle.
        if self.dir[1] > 0:  # right paddle
            print("moving towards right paddle")
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
            print("moving towards left paddle")
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
        elif y >= board_size - 1:  # Bottom wall
            self.y = board_size - 1
            self.dir[0] = -self.dir[0]  # Reverse vertical direction