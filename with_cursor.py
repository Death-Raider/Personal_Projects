"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
import numpy as np
import pyautogui

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

calibration_h = [0.37,0.66] # min, max
calibration_v = [0.57,0.65] # min, max

def calibrate_value(value,calibration_value_range,range=[0,1]):
    a,b = range
    c,d = calibration_value_range
    x = value
    return (x-c) * ((b-a)/(d-c)) + a

def draw_all_circles(frame,n,color = (255,255,255), alpha=0.9):
    frame_h , frame_w = frame.shape[:2]
    grid = np.zeros_like(frame)
    cell_width = int(frame_w/n)
    cell_height = int(frame_h/n)
    cell_center = np.array([cell_width/2, cell_height/2], dtype=int)
    axis_length = np.array([cell_width/2,cell_height/2],dtype=int)
    # print(frame_w,frame_h,cell_width,cell_height,cell_center,axis_length)

    for i in range(n):
        for j in range(n):
            offset = np.array([i*cell_width,j*cell_height],dtype=int)
            new_cell_center = cell_center + offset
            cv2.ellipse(grid,new_cell_center,axis_length,0,0,360,color,-1)
    grid_mask = grid.astype(bool)
    frame[grid_mask] = cv2.addWeighted(frame,alpha,grid,1-alpha,0)[grid_mask]
    return frame

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)
    frame = cv2.resize(frame,(1920,1080))
    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    ratiov = gaze.vertical_ratio()
    ratioh = gaze.horizontal_ratio()
    blink = gaze.is_blinking()

    if ratioh and ratiov:
        # ratiov -= 0.4
        # ratioh -= 0.1
        # text = f"ver:{ratiov:.2} hor:{ratioh:.2}"
        ratiov_cal = calibrate_value(ratiov, calibration_v)
        ratioh_cal = calibrate_value(ratioh, calibration_h)
        text = f"ver:{ratiov:.2}, {ratiov_cal:.2}   hor:{ratioh:.2}, {ratioh_cal:.2}"
        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
        screen_x = int((ratioh_cal)*1920)
        screen_y = int((ratiov_cal)*1080)

        if screen_x < 0:
            screen_x = 20
        if screen_y < 0:
            screen_y = 20
        if screen_x > 1920:
            screen_x = 1900
        if screen_y > 1080:
            screen_y = 1060

        cv2.circle(frame,(screen_x,screen_y),radius=10,color=(0,0,0), thickness=-1)
        if blink:
            # cv2.putText(frame, "Click", (1000, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            # pyautogui.dragTo(screen_x,screen_y)
            # pyautogui.sleep(0.5)
            pass
        pyautogui.dragTo(screen_x,screen_y,  button='left') # https://paper-io.com/

    # frame = draw_all_circles(frame,5,color=(0,0,255),alpha=0.2)
    # cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == ord('q'):
        break
   
webcam.release()
cv2.destroyAllWindows()