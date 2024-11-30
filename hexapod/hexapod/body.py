
class Body:
    """
        TODO: add wheel joints and other body parts to the whole body.
        Might require to have a seprate static initilization sequence for the body
    """
    def __init__(self):
        self.pos = [1.0, 0.0, 0.5]
        self.rot = [0.0, 0.0, 0.0, 1.0]
        self.radius = 2.0
        self.height = 1.0

    def increment_pos(self, dir_vec):
        self.pos[0] += dir_vec[0]
        self.pos[1] += dir_vec[1]
        self.pos[2] += dir_vec[2]