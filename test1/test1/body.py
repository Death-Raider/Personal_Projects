
class Body:
    def __init__(self):
        self.pos = [1.0,0.0,0.0]
        self.rot = [0.0,0.0,0.0,1.0]

    def increment_pos(self, dir_vec):
        self.pos[0] += dir_vec[0]
        self.pos[1] += dir_vec[1]
        self.pos[2] += dir_vec[2]