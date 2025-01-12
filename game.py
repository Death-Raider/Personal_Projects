import matplotlib.pyplot as plt
from board import Board
import keyboard

board = Board(size=100)
game = board.pong_game()

plt.ion()
while True:
    board_state, scores = next(game)
    plt.imshow(board_state, cmap="gray")
    plt.title(f"Scores - Left: {scores[1]} | Right: {scores[2]}")
    plt.pause(0.01)
    if keyboard.is_pressed('q'):
        plt.ioff()
        plt.show()
        break
    plt.clf()