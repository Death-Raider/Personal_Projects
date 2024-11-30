from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Annotator
from roboflow import Roboflow
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import json
# torch.backends.quantized.engine = 'qnnpack'


def download_Dataset():
    api_key_file = open("api_key.json").read()
    rf = Roboflow(api_key=json.loads(api_key_file)["api_key"])
    project = rf.workspace("oragimirox-gmail-com").project("plant_diseases-jczad")
    dataset = project.version(1).download("yolov8")

def train_model(model):
        results = model.train(data='datasets/Plant_Diseases-1/data.yaml',
                          epochs=40, batch=3, optimizer='Adam', device=0, cos_lr=True)
        return results

def realtime(model,cap,S,endtime = 10):
    
    FPS = cap.get(cv2.CAP_PROP_FPS)
    print(f"input video running at {FPS} frames per second")
    frames = []
    outframes = []
    times = []
    batch = int(S*FPS)
    iterator = 1
    print("Batch:",batch)
    cummulative_time = 0
    while True:
        if endtime*1000 <= cummulative_time: break
        ret, frame = cap.read()
        if not ret: break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb,(416,416))
        frames.append(frame_rgb)
        if iterator >= batch:
            t1 = time.time()
            result = model.predict(source = frames, verbose=False, device='cpu', imgsz = 416)
            # --------------------------- #
            # for i,r in enumerate(result):
            #     annotator = Annotator(frames[i])
            #     boxes = r.boxes
            #     for box in boxes:
            #         b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
            #         c = box.cls
            #         annotator.box_label(b, model.names[int(c)])
            #     frame = annotator.result()
            #     frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            #     outframes.append(frame)
            # --------------------------- #
            t2 = time.time()
            frames = []
            iterator = 0
            times.append((t2-t1)*1000)
            cummulative_time += (t2-t1)*1000
            # print((t2-t1)*1000,(t2-t1)*1000/batch)

        # if len(outframes) > 0:
        #     frame = outframes.pop(0)
        #     cv2.imshow('YOLO V8 Detection', frame)     
        # if cv2.waitKey(1) & 0xFF == ord(' '):
        #     break
        iterator+=1

    avg_times = sum(times)/len(times)
    print("batch infrence time:", avg_times,"ms")
    print("per image infrence time:", avg_times/batch,"ms")
    return avg_times/batch

if __name__ == '__main__':
    net = YOLO('yolov8m.pt')
    model = net
    cap = cv2.VideoCapture(0)
    t1 = time.time()
    model.predict(source = np.zeros((416,416,3)), verbose = False, device = 'cpu', imgsz = 416)
    t2 = time.time()-t1
    print("warmup time:",t2, "s")

    time_arr = []
    point_count = 30
    time_consideration = 5 # seconds
    for n in range(1,point_count):
        time_arr.append(realtime(model,cap,n/30,time_consideration))
    cap.release()

    plt.figure()
    plt.plot(list(range(1,point_count)),time_arr)
    plt.xlabel("batch size")
    plt.ylabel("inference time (ms)")
    plt.grid()
    plt.show()

