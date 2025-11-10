import numpy as np
import pandas as pd
import GoalChasing_QLearning.single_DQagent as GC_QL
import time

threshold = 10
state_dim = (2*threshold+1) * (2*threshold+1) * 2 + 2 
action_dim = 8
start_id = 6
agent: GC_QL.DQAgent = GC_QL.DQAgent(
    state_dim=state_dim, 
    action_dim=action_dim, 
    lr=0.0,
    gamma=0.90,                    # Prioritize short-term rewards
    epsilon_decay=0.9998,           # Slower exploration decay
    memory_size=20000, 
    target_update_freq = 1000,
)

ROBOT_COUNT_RANGE = [
    5,     10,     15,     20,     25,     30]
BOARD_SIZE_RANGE =  [
    50,    60,    70,     80,     90,     100]

EVALUATION_MATRIX = np.zeros((len(ROBOT_COUNT_RANGE), len(BOARD_SIZE_RANGE)))
eval_df = pd.DataFrame(EVALUATION_MATRIX.copy(), index=ROBOT_COUNT_RANGE, columns=BOARD_SIZE_RANGE)
eval_2_df = pd.DataFrame(EVALUATION_MATRIX.copy(), index=ROBOT_COUNT_RANGE, columns=BOARD_SIZE_RANGE)
values = GC_QL.load_model_and_data(agent, 'x9')

def trivial_action(board: GC_QL.Board, curr_states: list):
    actions = []
    for i,[r,g,a] in enumerate(board.players):
        dist, angle = r.get_dist(g)
        angle_deg = angle * 180/np.pi
        angle_binary = np.argmin([abs(DIR - angle_deg) for DIR in r.DIR_ANGLES])
        # print( angle, angle_deg, r.DIR_ANGLES, angle_binary)
        action = angle_binary # a.choose_action(curr_states[i])
        actions.append(action)
        r._set_dir(action)
    return actions

for rc in ROBOT_COUNT_RANGE:
    for bs in BOARD_SIZE_RANGE:

        board_size = bs
        robot_count = rc

        board = GC_QL.Board(board_size)

        epch = 10

        agent.epsilon = 0.01
        col, *_, dones = GC_QL.run(board, threshold, robot_count, board_size, agent, epch, TRAIN=False, SHOW=True, SHOW_LAST_EPOCH=False, SAVE_EVERY_EPOCH=False, 
                    agent_directory='xx', OVERRIDE_ACTIONS=None)
        time.sleep(0.1)
        eval_df.loc[rc, bs] = col.sum()/dones.sum()
        eval_2_df.loc[rc, bs] = np.sqrt(dones * (col/dones - eval_df.loc[rc, bs])**2).sum() / dones.sum()
        print("Average collision over all robot over all epochs:", np.round(eval_df.loc[rc, bs],2), "with std:", np.round(eval_2_df.loc[rc, bs],2))

eval_df.to_csv("GoalChasing_QLearning/x_evaluation_trivial.csv")
eval_2_df.to_csv("GoalChasing_QLearning/x_evaluation_trivial_std.csv")