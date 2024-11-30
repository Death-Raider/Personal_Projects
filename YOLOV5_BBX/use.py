import os
path = r"Images_resize/test.png"
cmd = f"python yolov5/detect.py --source {path} --weights best.pt --img 416 --conf-thres 0.2 --line-thickness 1 --project Output"
os.system(cmd)
