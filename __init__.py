# from Runners.GoalChasing_QLearning.DQ_learning import *
from Runners.Pong_QLearning.Q_learning import *

# agent1.load_model('saved_models/agent1_epoch_final')
# agent1.epsilon = 0.1  # Set epsilon to 0 for evaluation (fully greedy)
# agent2.load_model('saved_models/agent2_epoch_final')
# agent2.epsilon = 0.1  # Set epsilon to 0 for evaluation (fully greedy)

metrics = run_game(
    default_board, 
    {'agent1': agent1, 'agent2': agent2}, 
    epochs=1000, 
    SHOW_LAST_EPOCH=True, 
    SAVE_METRICS=False,
    save_models=False,
    save_model_freq=100,
    max_steps_per_episode=5000,
    verbose=1,
    render = False,
)

import matplotlib.pyplot as plt
import pandas as pd
import json

agent1_metrics = {
    'reward' : [m['agent1'] for m in metrics['rewards']],
    'loss' : [m['agent1'] for m in metrics['losses']],
}
agent2_metrics = {
    'reward' : [m['agent2'] for m in metrics['rewards']],
    'loss' : [m['agent2'] for m in metrics['losses']],
}
episode_lengths = metrics['episode_lengths']

df1 = pd.DataFrame(agent1_metrics)
df2 = pd.DataFrame(agent2_metrics)
plt.figure()
plt.plot(df1['reward'], label='Agent 1 Reward')
plt.plot(df2['reward'], label='Agent 2 Reward')
plt.legend()
plt.show()
plt.figure()
plt.plot(df1['loss'], label='Agent 1 Loss')
plt.plot(df2['loss'], label='Agent 2 Loss')
plt.show()
plt.plot(range(len(episode_lengths)), episode_lengths)
plt.show()

# from Runners.GoalChasing_QLearning.Q_learning import *
# from Runners.GoalChasing_QLearning.CADRL_Learning import *
# from Runners.GoalChasing_QLearning.collision_evaluation import *

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