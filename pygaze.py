import cv2
import numpy as np
from gaze_tracking import GazeTracking
import time

def calibrate_value(value,calibration_value_range,range=[0,1]):
    a,b = range
    c,d = calibration_value_range
    x = value
    return (x-c) * ((b-a)/(d-c)) + a

def draw_grid(frame,n,color = (255,255,255), alpha=0.9):
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

def draw_circle(frame,n,point,color,alpha):
    grid = np.zeros_like(frame)
    frame_h , frame_w = frame.shape[:2]
    point_x, point_y = point
    cell_w, cell_h = int(frame_w/n), int(frame_h/n)
    center = np.array([cell_w/2,cell_h/2],dtype=int)

    N_x = int(np.ceil((point_x)/cell_w) - 1)
    N_y = int(np.ceil((point_y)/cell_h) - 1)

    center_point = center + np.array([N_x*cell_w,N_y*cell_h],dtype=int)

    cv2.ellipse(
                    grid,
                    center=center_point,
                    axes=center,
                    angle=0,
                    startAngle=0,
                    endAngle=360,
                    color=color,
                    thickness=-1
                )
    grid_mask = grid.astype(bool)

    frame[grid_mask] = cv2.addWeighted(frame,alpha,grid,1-alpha,0)[grid_mask]
    return N_x, N_y

def main():
    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0)
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000,1000
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    set_values=  []

    calibration_h = [0.5,0.8] # min, max
    calibration_v = [0.7,0.8] # min, max 
    while True:
        # We get a new frame from the webcam
        _, frame = webcam.read()
        frame = cv2.flip(frame,1)
        frame = cv2.resize(frame,(SCREEN_WIDTH,SCREEN_HEIGHT))
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

            screen_x = int((ratioh_cal)*SCREEN_WIDTH)
            screen_y = int((ratiov_cal)*SCREEN_HEIGHT)

            if screen_x < 0:
                screen_x = 20
            if screen_y < 0:
                screen_y = 20
            if screen_x > SCREEN_WIDTH:
                screen_x = SCREEN_WIDTH-20
            if screen_y > SCREEN_WIDTH:
                screen_y = SCREEN_HEIGHT-20

            # cv2.circle(frame,(screen_x,screen_y),radius=15,color=(255,255,255), thickness=-1)
        N = 50
        frame = draw_grid(frame,N,color=(0,0,255),alpha=0.6)
        Nx,Ny = draw_circle(frame,N,(screen_x, screen_y),(255,0,0),0.1)
        time.sleep(0.1)

        # if blink:
        #     # print("blinked",Nx,Ny)
        #     add = True
        #     for x,y,nx,ny in set_values:
        #         add = add and not ( nx == Nx and ny == Ny)
        #         # print("set_vals",nx,ny)
        #     if add:
        #         set_values.append([screen_x, screen_y, Nx, Ny])
        # for x,y,_,_ in set_values:
        #     draw_circle(frame,N,(x, y),(255,255,155),0.5)

        frame = cv2.resize(frame,(1920,1080)) 
        cv2.imshow("img", frame)
        if cv2.waitKey(1) == ord('q'):
            break
    
    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()