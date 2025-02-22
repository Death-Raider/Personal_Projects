# Train the model on the obtained dataset.npy

import pandas as pd
import random
from sklearn.model_selection import train_test_split
import Pong_QLearning.D_Q_learning as DQL
np = DQL.np
tf = DQL.tf
keras = DQL.keras
plt = DQL.plt

# DQL.max_val   # (y1, y2, by, bx, a)
def load_from_npy():
    with open("Pong_QLearning/data/dataset.npy", 'rb') as file:
        dataset = np.load(file,allow_pickle=True).tolist()

    dataset_list = []

    for agent in range(len(dataset)):
        print("Length of data",len(dataset[agent]))
        for i in range(len(dataset[agent])):
            curr_state = np.round(dataset[agent][i]['current_state'],3).tolist()
            action = dataset[agent][i]['action']
            reward = dataset[agent][i]['reward']
            next_state = np.round(dataset[agent][i]['next_state'],3).tolist()
            combined_states = [agent,*curr_state,action,reward,*next_state]
            dataset_list.append(combined_states)

    return dataset_list

def test_state(state, simulation_time):
    DQL.board.set_state(state)
    DQL.board.update()
    for i in range(simulation_time):
        plt.imshow(DQL.board.board)
        DQL.board.ball.move(DQL.board.l_paddle, DQL.board.r_paddle, DQL.board)
        DQL.board.update()
        print(DQL.board.current_board_state())
        plt.pause(0.1)
    plt.show()

def visulize_row(data):
    random_state = data.loc[random.randint(0,len(data)-1)]
    curr_state = random_state[1:6]
    next_state = random_state[8:]
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)

    DQL.board.set_state(curr_state)
    DQL.board.update()
    ax1.imshow(DQL.board.board)
    ax1.set_title('curr_state\n'+','.join(map(str,curr_state)))

    DQL.board.set_state(next_state)
    DQL.board.update()
    ax2.imshow(DQL.board.board)
    ax2.set_title('next_state\n'+','.join(map(str,next_state)))
    plt.show()

CURR_STATE = ['curr_y1','curr_y2','curr_bx','curr_by','curr_a']
NEXT_STATE = ['next_y1','next_y2','next_bx','next_by','next_a']

agent_data = pd.DataFrame( data=load_from_npy(), columns=[
    'agent',
    *CURR_STATE,  # curr_state
    'action',
    'reward',
    *NEXT_STATE,  # next_state
])

# agent_data = pd.read_csv("Pong_QLearning/data/data.csv",index_col='Unnamed: 0')
# agent_data.to_csv("Pong_QLearning/data/data.csv", index=False)

print(agent_data.head())
print(agent_data.describe())
visulize_row(agent_data)

agent_1_data = agent_data[agent_data['agent']==0]
agent_2_data = agent_data[agent_data['agent']==1]
print(agent_1_data.describe())
print(agent_2_data.describe())

col = 'reward'
moving_avg = agent_1_data[col].rolling(window=1000).mean()
plt.plot(agent_1_data[col], label='Reward Data', alpha=0.5)
plt.plot(moving_avg, label=f'Moving Average (window={1000})', color='red', linewidth=2)
plt.show()
plt.hist(agent_1_data[col], bins=50, edgecolor='black')
plt.show()

moving_avg = agent_2_data[col].rolling(window=1000).mean()
plt.plot(agent_2_data[col], label='Reward Data', alpha=0.5)
plt.plot(moving_avg, label=f'Moving Average (window={1000})', color='red', linewidth=2)
plt.show()
plt.hist(agent_2_data[col], bins=50, edgecolor='black')
plt.show()

# DQL.agent1.model = keras.saving.load_model('Pong_QLearning/models/Agent_1.keras')
# DQL.agent2.model = keras.saving.load_model('Pong_QLearning/models/Agent_2.keras')
