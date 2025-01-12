import matplotlib.pyplot as plt
from board import Board

board = Board(size=100)
game = board.pong_game()

plt.ion()
for _ in range(100):
    board_state = next(game)
    plt.imshow(board_state)
    plt.pause(0.01)
    plt.clf()

plt.ioff()
plt.show()