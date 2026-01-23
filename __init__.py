# import Runners.GoalChasing_QLearning.evaluations.optimizer as opt
# import GoalChasing_QLearning.evaluations.case_study as GC_CaseStudy
# import GoalChasing_QLearning.evaluations.evaluate_collision as eval_collision

# from Runners.Pong_QLearning.Q_learning import * 
# run_game(default_board, {'agent1': agent1, 'agent2': agent2}, epochs=1000, SHOW_LAST_EPOCH=True, SAVE_METRICS=False,)

# from Runners.GoalChasing_QLearning.Q_learning import *
# from Runners.GoalChasing_QLearning.CADRL_Learning import *
from Runners.GoalChasing_QLearning.collision_evaluation import *

# import os
# import json
# import tensorflow as tf
# from keras.models import Model, Sequential
# from keras.layers import Input, Dense


# directory = r'./Runners/GoalChasing_QLearning/results/DQL_Agent'
# os.mkdir(directory)

# with open(f"{directory}/metrics.json", 'w') as f:
#     json.dump('Hiii', f, indent=2)

# m = Sequential([
#     Input(shape=(10,)),\
#     Dense(units=9)
# ])
# m.save(directory+"/model.keras")

"""
Tasks Completed:
- Created Goal Chasing Environment and Vislization
- High level work description
- Dataset description
- Q-Learning Description
- PlantUML Class Diagram for this work

"""