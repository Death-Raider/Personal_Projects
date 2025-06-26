import GoalChasing_QLearning.single_DQagent as GC_QL
import numpy as np
import matplotlib.pyplot as plt
threshold = 10
state_dim = (2*threshold+1) * (2*threshold+1) * 2 + 2 
action_dim = 8

board_size = 20

board = GC_QL.Board(board_size)

agent: GC_QL.DQAgent = GC_QL.DQAgent(
    state_dim=state_dim, 
    action_dim=action_dim, 
    lr=0.001,
    gamma=0.90,                    # Prioritize short-term rewards
    epsilon_decay=0.9998,           # Slower exploration decay
    memory_size=2000, 
    target_update_freq = 100,
)
agent.epsilon = 0.01
GC_QL.load_model_and_data(agent, 't9')

GC_QL.run(board, threshold, 5, board_size, agent, 100, True, False, False, True, 't10')
#Dual Robot Cases
# dir can be one of the 8 directions: [NE, N, NW, E, W ,SE, S, SW]
R1 = GC_QL.Robot(
    id=1,
    x=0, 
    y=board_size//2-3, 
    h=1, 
    w=1, 
    a=0,
    v=1, 
    dir=3,  # E
    cooperation=0,
    view_threshold=threshold,
    closeness_threshold=threshold//3
)
G1 = GC_QL.Goal(
    id=1,
    x=board_size-3,
    y=board_size//2-3,
    value=1
)
R2 = GC_QL.Robot(
    id=2,
    x=board_size-1, 
    y=board_size//2 - 3, 
    h=1, 
    w=1, 
    a=0,
    v=1, 
    dir=3,  # E
    cooperation=0,
    view_threshold=threshold,
    closeness_threshold=threshold//3
)
G2 = GC_QL.Goal(
    id=2,
    x=3,
    y=board_size//2+1,
    value=1
)
board.players = []
board.add_robot(R1, G1, agent)
board.add_robot(R2, G2, agent)

GC_QL.set_board(board)
plt.imshow(board.board, cmap='gray', vmin=-2, vmax=2)

EPOCHS = 1
iter = 0
done = False

robot_count = len(board.players)
board.max_players = robot_count

reward_dataset = [[0]*EPOCHS for i in range(robot_count)]
loss_dataset = [[0]*EPOCHS for i in range(robot_count)]

curr_states = GC_QL.get_curr_state(board)

while not done:
    iter, reward_dataset, loss_dataset, curr_states,actions, move_success, new_states, collisions, rewards, done = GC_QL.game_loop(
                                                                                                                    board, 
                                                                                                                    board_size, 
                                                                                                                    curr_states, 
                                                                                                                    iter, 
                                                                                                                    0, # current_epoch
                                                                                                                    reward_dataset, 
                                                                                                                    loss_dataset, 
                                                                                                                    done, 
                                                                                                                    False # train
                                                                                                                )
    print(collisions, rewards)
    print(len(board.players))
    plt.imshow(board.board, cmap='gray', vmin=-2, vmax=2)
    plt.pause(0.5)
plt.show()  