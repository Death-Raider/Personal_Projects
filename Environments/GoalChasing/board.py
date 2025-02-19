from Environments.GoalChasing.robot import Robot
from Environments.GoalChasing.goal import Goal

import numpy as np

class Board:
    def __init__(self, size: int = 100):
        self.size = size
        self.board = np.zeros((size,size))
        self.players: list[list[Robot,Goal]]  = []
    
        self.action_map = {
            "up": 0, 
            "down": 1, 
            "right": 2,
            "left": 3
        }
        self.dist_table: np.ndarray = np.zeros((1,1,2))

    # def update_dist_table(self):
    #     players = self.players

    #     if self.dist_table.shape[0] != len(players):
    #         self.dist_table = np.zeros((len(players), len(players), 2),dtype=float)
        
    #     for i in range(len(players)):
    #         for j in range(len(players)):
    #             self.dist_table[i,j,:] = players[i][0].get_dist(players[j][0])
    
    def update_views(self):
        for p,g in self.players:
            thresh = int(p.closeness_threshold)
            x = int(p.x)
            y = int(p.y)
            arr = self.board[y-thresh:y+thresh+1, x-thresh:x+thresh+1]
            new_arr = np.pad(arr, ((0,7-arr.shape[0]), (0,7-arr.shape[1])), mode='constant')
            p.view = new_arr

    def update_robots(self):
        self.players = [[r,g] for i,[r,g] in enumerate(self.players) if r.get_dist([g.y,g.x])[0] > 1]
    
    def get_robot_by_id(self, id):
        for p,g in self.players:
            if p.id == id:
                return p
        return None
        
    def delete_robot(self, player_index):
        self.players.pop(player_index)

    def add_robot(self, robot: Robot, goal: Goal):
        self.players.append([robot,goal])
    
    def draw_board(self):
        # goal -> -1, -2, -3, ..., -id
        # robot -> 1,2,3, ..., id
        self.board = np.zeros((self.size, self.size))
        for [p,g] in self.players:
            self.board[int(p.y), int(p.x)] = int(p.id)
            self.board[int(g.y), int(g.x)] = - int(g.id)