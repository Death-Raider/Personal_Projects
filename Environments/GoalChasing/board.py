from robot import Robot
from goal import Goal

import numpy as np

class Board:
    def __init__(self, size: int = 100):
        self.size = size
        self.board = np.zeros_like((size,size))
        self.players = {}

    def add_robot(self, robot: Robot, goal: Goal):
        assert robot.id == goal.id
        self.players[robot['id']] = [robot,goal]