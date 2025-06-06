# import GoalChasing_QLearning.optimizer as opt  # optimization is done
import numpy as np
import pandas as pd
import GoalChasing_QLearning.single_DQagent as GC_QL

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
    memory_size=2000, 
    target_update_freq = 100,
)

ROBOT_COUNT_RANGE = [5,     10,     15,     20,     25,     30]
BOARD_SIZE_RANGE =  [50,    60,     70,     80,     90,     100]

EVALUATION_MATRIX = np.zeros((len(ROBOT_COUNT_RANGE), len(BOARD_SIZE_RANGE)))
eval_df = pd.DataFrame(EVALUATION_MATRIX, index=ROBOT_COUNT_RANGE, columns=BOARD_SIZE_RANGE)
values = GC_QL.load_model_and_data(agent, 't9')

for rc in ROBOT_COUNT_RANGE:
    for bs in BOARD_SIZE_RANGE:

        board_size = bs
        robot_count = rc

        board = GC_QL.Board(board_size)

        epch = 10
        TRAIN = False
        SHOW = True
        SHOW_LAST_EPOCH = False
        agent.epsilon = 0.01
        col, _, _ = GC_QL.run(board, threshold, robot_count, board_size, agent, epch, TRAIN=TRAIN, SHOW=False, SHOW_LAST_EPOCH=SHOW_LAST_EPOCH, SAVE_EVERY_EPOCH=False, 
                    agent_directory='xx')
        eval_df.loc[rc, bs] = col.mean()
        print("Average collision over all robot over all epochs:", np.round(col.mean(),2), "with std:", np.round(col.std(),2))

eval_df.to_csv("evaluation.csv")
# col = np.array(col)
# print("Average collision per robot:", col.mean(axis = 1))

"""
Tasks Completed:
- Created Goal Chasing Environment and Vislization
- High level work description
- Dataset description
- Q-Learning Description
- PlantUML Class Diagram for this work

"""