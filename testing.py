import threading
import pyautogui

class GameState:
  def __init__(self):
    self.DIR_KEYS = {
      "up": "w",
      "left": "a",
      "down": "s",
      "right": "d"
    }

  def move(self, direction):
    pyautogui.keyDown(self.DIR_KEYS[direction])

  def unmove(self, direction):
    pyautogui.keyUp(self.DIR_KEYS[direction])

class Move:
  def __init__(self, state, direction, delay):
    self.state = state
    self.direction = direction
    self.delay = delay

  def execute(self,direction=None):

    if direction != None: self.direction = direction;
    self.state.move(self.direction)
    threading.Timer(self.delay, self.undo).start()

  def undo(self):
    self.state.unmove(self.direction)

state = GameState()
Move(state, "up", 1.0).execute()
