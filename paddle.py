class Paddle:
    def __init__(self, length=5, x=0, y=0):
        self.length = length
        self.x = x
        self.y = y

    def move(self, direction, board_size):
        new_pos = self.y + direction
        if 0 <= new_pos <= board_size - self.length:
            self.y = new_pos