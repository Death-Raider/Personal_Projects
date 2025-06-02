# import GoalChasing_QLearning.multi_DQagent_FederatedLearning as GC_QL
import GoalChasing_QLearning.single_DQagent as GC_QL
import numpy as np

# Parameters for training and evaluation
SHOW = False
SHOW_LAST_EPOCH = False
TRAIN = True
LOAD_MODEL = True
EPOCHS = 120

robot_count = 20
board_size = 100
threshold = 10
state_dim = (2*threshold+1) * (2*threshold+1) * 2 + 2 
action_dim = 8
agent_directory = "t1"
board = GC_QL.Board(board_size)

# create the agents
agent: GC_QL.DQAgent = GC_QL.DQAgent(
    state_dim=state_dim, 
    action_dim=action_dim, 
    lr=1e-3,
    gamma=0.90,                    # Prioritize short-term rewards
    epsilon_decay=0.9998,           # Slower exploration decay
    memory_size=2000, 
    target_update_freq = 100,
)

if LOAD_MODEL:
    if TRAIN:
        agent.epsilon = 0.4  # Set a higher exploration rate for training
    else:
        agent.epsilon = 0.01  # Set a low exploration rate for evaluation
    states, actions, rewards, next_states, dones = GC_QL.load_model_and_data(agent, agent_directory)
    loss = agent.evaluate(states, actions, rewards, next_states, dones)
    print("reward", rewards.mean())
    print("Loss on loaded data:", loss)

GC_QL.run(board, threshold, robot_count, board_size, agent, EPOCHS, TRAIN=TRAIN, SHOW=SHOW, SHOW_LAST_EPOCH=SHOW_LAST_EPOCH)

"""
Tasks Completed:
- Created Goal Chasing Environment and Vislization
- High level work description
- Dataset description
- Q-Learning Description
- PlantUML Class Diagram for this work

"""