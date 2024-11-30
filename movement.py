import time
import pyautogui
import math

class Game_State:
    def __init__(self):
        self.List = []
        self.currentList = []
    def parse(self): # TODO: fix for clicking function
        for i, state_list in enumerate(self.List):
            state_list = sorted(state_list, key=lambda k: k["duration"])
            #---------------key hold--------------------#
            for state in state_list:
                if "hotbar" in state:
                    pyautogui.press(state["hotbar"])
                if "direction" in state:
                    pyautogui.keyDown(state["direction"])
                else:
                    pyautogui.keyDown(state["key"])
            #-------------unhold key-------------------#
            clickingState = next( ( (i,d) for i,d in enumerate(state_list) if "interval" in d), None)
            timePassed = 0
            for i, state in enumerate(state_list):
                delay = state["duration"]-timePassed
                timePassed = state["duration"]
                if clickingState != None and i <= clickingState[0] :
                    pyautogui.press(clickingState[1]["key"], interval = clickingState[1]["interval"], presses = round(clickingState[1]["bps"]*delay) )
                else:
                    time.sleep(delay)
                print(timePassed, state)
                if "direction" in state:
                    pyautogui.keyUp(state["direction"])
                else:
                    pyautogui.keyUp(state["key"])

    def then(self):
        self.List.append(self.currentList)
        self.currentList = []
    def create_list(self,*states):
        for state in states: self.currentList.append(state)
    def view_deg(self, deg, dir):
        view = {}
        view["duration"] =  round(13*deg/1200,3)
        view["direction"] = dir
        return view
    def move_by_block(self, blc, dir):
        dir = "w" if dir == "up" else "s" if dir == "down" else "a" if dir == "left" else "d"
        movement = {}
        movement["duration"] = round(blc/4.317,3)
        movement["direction"] = dir
        return movement
    def special_key_tap(self, n, s, i, key):
        interact = {}
        interact["key"] = key
        interact["duration"] = round(n/s,3)
        interact["interval"] = 1/s
        interact["bps"] = s
        interact["quantity"] = n
        interact["hotbar"] = str(i)
        return interact
    def special_key_hold(self,key,duration):
        special = {}
        special["key"] = key
        special["duration"] = duration
        return special
"""
given a point on the screen A and its distance from the center "d" then the rotational angle = 2 asin( d/(2r) )
where r is the reach = 5
"""
Game = Game_State()
view1 = Game.view_deg(90,"left")
move1 = Game.move_by_block(10,"up")
move2 = Game.move_by_block(9,"up")
tap1 = Game.special_key_tap(2,100,1,"w")
hold1 = Game.special_key_hold("space",2)
sprint = Game.special_key_hold("ctrl",2)


Game.create_list(sprint,move1,hold1)
Game.then()
Game.create_list(view1)
Game.then()
Game.create_list(sprint,move2,hold1)
Game.then()

time.sleep(2)
Game.parse()
