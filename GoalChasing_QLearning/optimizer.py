# import GoalChasing_QLearning.multi_DQagent_FederatedLearning as GC_QL
import GoalChasing_QLearning.single_DQagent as GC_QL
import numpy as np

# Parameters for training and evaluation
SHOW = False
SHOW_LAST_EPOCH = False
TRAIN = True
LOAD_MODEL = False
# EPOCHS = 120
INDEXES =       [0,     1,      2,      3,      4,      5,      6,      7,      8,      9   ]
ROBOT_COUNTS =  [10,    20,     30,     10,     20,     40,     10,     20,     30,     50  ]
BOARD_SIZES =   [50,    100,    100,    40,     60,     100,    40,     50,     60,     100 ]
LRS =           [1e-3,  1e-4,   1e-5,   1e-3,   1e-4,   1e-5,   1e-3,   1e-4,   1e-4,   1e-5]
INIT_EPSILONS = [1.0,   0.4,    0.2,    0.4,    0.2,    0.1,    0.4,    0.2,    0.1,    0.05]
EPOCHS =        [40,    60,     54,     40,     60,     54,     40,     60,     54,     54 ]

threshold = 10
state_dim = (2*threshold+1) * (2*threshold+1) * 2 + 2 
action_dim = 8
start_id = 6

for id, rc, bs, lr, epsilon, epch in zip(INDEXES, ROBOT_COUNTS, BOARD_SIZES, LRS, INIT_EPSILONS, EPOCHS):
    if id < start_id:
        continue

    robot_count = rc
    board_size = bs
    board = GC_QL.Board(board_size)
    load_agent_directory = f"t{id-1}"
    save_agent_directory = f"t{id}"
    # create the agents
    agent: GC_QL.DQAgent = GC_QL.DQAgent(
        state_dim=state_dim, 
        action_dim=action_dim, 
        lr=lr,
        gamma=0.90,                    # Prioritize short-term rewards
        epsilon_decay=0.9998,           # Slower exploration decay
        memory_size=2000, 
        target_update_freq = 100,
    )

    if id != 0:
        agent.epsilon = epsilon
        GC_QL.load_model_and_data(agent, load_agent_directory)
        # loss = agent.evaluate(states, actions, rewards, next_states, dones, batch=128)
        # print("reward", rewards.mean())
        # print("Loss on loaded data:", loss)

    GC_QL.run(board, threshold, robot_count, board_size, agent, epch, TRAIN=TRAIN, SHOW=SHOW, SHOW_LAST_EPOCH=SHOW_LAST_EPOCH, SAVE_EVERY_EPOCH=True, 
              agent_directory=save_agent_directory)
    GC_QL.save_model_and_data(agent, save_agent_directory)


