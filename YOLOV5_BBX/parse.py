import cv2
import os
import time
from PIL import ImageGrab
import numpy as np
import torch
# https://stackoverflow.com/questions/61723675/crop-a-video-in-python

def getImagesGen(length):
    for i in range(length):
        img = np.array(ImageGrab.grab(bbox=(0,50,1920,950)))
        img = cv2.resize(img,(416,416),interpolation = cv2.INTER_AREA)
        yield img
        # cv2.imwrite(f"Images_resize_new/{100+i}.png", img)

def load_model(yolo_path,weight_path):
    model = torch.hub.load(yolo_path, 'custom', path=weight_path, source="local")
    return model

def predict(length):
    model = load_model("yolov5","best.pt")
    imgs = []
    for i in range(length):
        imgs.append( cv2.cvtColor(cv2.imread(f"Images_resize_new/{68+i}.png"), cv2.COLOR_BGR2RGB)  )
    out = model(imgs)
    out.print()
    out.save("Output",line_width = 1)

def predictVid(file):
    os.system(f"python yolov5/detect.py --source {file} --weights best.pt --imgsz 416 --line-thickness 1 --conf-thres 0.2 --project Output")
def reshapeVid(file):
    # Open the video
    cap = cv2.VideoCapture(file)
    # Initialize frame counter
    cnt = 0
    w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Some characteristics from the original video
    fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # Here you can define your croping values
    x,y,h,w = 0,50,416,416
    # output
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('result.avi', fourcc, fps, (w, h))

    # Now we start
    while(cap.isOpened()):
        ret, frame = cap.read()
        cnt += 1 # Counting frames
        # Avoid problems when video finish
        if ret==True:
            # Croping the frame
            crop_frame = frame[y:y+920, x:x+1920]
            crop_frame = cv2.resize(crop_frame,(416,416),interpolation = cv2.INTER_AREA)
            # Percentage
            xx = cnt *100/frames
            print(int(xx),'%')
            out.write(crop_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# predictVid("result.avi")
# reshapeVid(r"C:\Users\oragi\Videos\Captures\Minecraft.mp4")

# python run.py
