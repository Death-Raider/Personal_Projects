import numpy as np
import time
import json
import cv2

SCREEN_HEIGHT, SCREEN_WIDTH = 1080 , 1920

class Calibrator:
    def __init__(self,mesurement_rate = 0.01): # 
        self.calls = 0
        self.measurement_rate = mesurement_rate # in seconds
        self.calibration_pos = {
            "center": 100, # num of calls for measurement
            "Tright": 100,
            "Bright": 100,
            "Tleft": 100,
            "Bleft": 100
        }
        self.total_calls = np.cumsum(list(self.calibration_pos.values())).tolist()
        self.total_calls.insert(0,0)
        self.calibration_results = {
            "center": [], # (self.calibration_pos["center"],2) before compress and after compress its (2,2)
            "Tright": [],
            "Bright": [],
            "Tleft": [],
            "Bleft": []
        }
        self.calibration_true_values = {
            "center": [int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2)],
            "Tright": [SCREEN_WIDTH, 0],
            "Bright": [SCREEN_WIDTH, SCREEN_HEIGHT],
            "Tleft": [0, 0],
            "Bleft": [0, SCREEN_HEIGHT],
        }
        self.calibration_status = False

        self.pretty_print_counter = -1 # part of the calibrate function

    def draw_solid_circle(self,frame,pos,r=35,color=(0,0,0)):# pos = (x,y)
        cv2.circle(frame,center=pos,radius=r,color=color,thickness=-1)
        return frame
    
    def calibrate(self,eye_pos,frame,draw=False):
        if len(eye_pos) == 2:
            if self.calls >= self.total_calls[-1] and not self.calibration_status:
                self.calibration_status = True
            else:
                for i,pos in enumerate(self.calibration_pos.keys()):
                    if self.total_calls[i] < self.calls < self.total_calls[i+1]:
                        if self.pretty_print_counter != i:
                            print("Look at the",pos,"of the screen", self.calls)
                            self.pretty_print_counter = i
                        time.sleep(self.measurement_rate)
                        self.calibration_results[pos].append(eye_pos)
                        # cv2.imwrite(f"test_img/{pos}.png",frame)               
                        if draw:
                            self.draw_solid_circle(frame,self.calibration_true_values[pos],color=(255,255,255))
                self.calls += 1
        return self.calibration_status
    
    def compress_calibrations(self):
        for key in self.calibration_results.keys():
            self.calibration_results[key] = np.array(self.calibration_results[key])
            self.calibration_results[key] = self.calibration_results[key].mean(axis=0).astype(int).tolist()

    def get_bounding_eye(self):
        all_pos = []
        for k in self.calibration_results.keys():
            all_pos.append(self.calibration_results[k])
        all_pos = np.array(all_pos)
        # print(all_pos.max(axis=2),all_pos.shape)
        max_eye = all_pos.max(axis=0)
        min_eye = all_pos.min(axis=0)
        return [*max_eye, *min_eye]
        
    def find_point_on_screen_linear(self,frame,p_eye,face_box):
        correction_offset = 0
        face_h,face_w = face_box
        frame_h, frame_w, frame_c = frame.shape
        r_max,l_max,r_min,l_min = self.get_bounding_eye()
        # eye_box = [
        #     [r_min[0],r_min[1],r_max[0]-r_min[0],r_max[1]-r_min[1]]
        #     [l_min[0],l_min[1],l_max[0]-l_min[0],l_max[1]-l_min[1]]
        #            ]

        out = []
        for index,eye_pos in enumerate(p_eye):
            (x0,y0) = self.calibration_results["center"][index]
            calibration_box_w = 300 #self.calibration_results["Bright"][index][0] - self.calibration_results["Tleft"][index][0] + correction_offset
            calibration_box_h = 300 #self.calibration_results["Bright"][index][1] - self.calibration_results["Tleft"][index][1] + correction_offset
            # ratio_to_eye_box = 
            ratio_to_face_box_X, ratio_to_face_box_Y = face_w/calibration_box_w, face_h/calibration_box_h
            ratio_to_frame_X, ratio_to_frame_Y = frame_w/face_w, frame_h/face_h

            x,y = ratio_to_face_box_X*ratio_to_frame_X*(eye_pos[0]), ratio_to_face_box_Y*ratio_to_frame_Y*(eye_pos[1])

            if  (0 < x < frame_w) and (0 < y < frame_h):
                out.append([x,y])
                # self.draw_solid_circle(frame,(int(x),int(y)),color=(0,255,0))
            else:
                out.append([0,0])
        return out

    def find_point_on_screen_polar(self,frame,p_eye): #p_eye = [[r_x,r_y],[l_x,l_y]]
        (x_true_center,y_true_center) = self.calibration_true_values["center"]

        outputs = []
        eye_index = 0
        for eye_index in range(1):

            (x0,y0) = self.calibration_results["center"][eye_index]

            px,py = p_eye[eye_index][0] - x0, p_eye[eye_index][1] - y0

            quadrant_names = ["center","Tright","Tleft","Bleft","Bright"]

            if px == 0 and py == 0:
                multiplier = [0,0]
                quadrant = 0
            elif px >= 0  and py >= 0:
                multiplier = [1,1]
                quadrant = 1
            elif px <= 0 and py >= 0:
                multiplier = [-1,1]
                quadrant = 2
            elif px <= 0 and py <= 0:
                multiplier = [-1,-1]
                quadrant = 3
            else:
                multiplier = [1,-1]
                quadrant = 4
            # if eye_index == 0: cv2.putText(frame,quadrant_names[quadrant],(200, 200),cv2.FONT_HERSHEY_DUPLEX,3.0, color = (125, 246, 55), thickness = 3)
            (x_q,y_q) = self.calibration_results[quadrant_names[quadrant]][eye_index]
            (x_true_quadrant,y_true_quadrant) = self.calibration_true_values[quadrant_names[quadrant]]

            x_eye, y_eye = x_q - x0, y_q - y0
            x_true_relative,y_true_relative = x_true_quadrant - x_true_center , y_true_quadrant - y_true_center

            if x_true_relative != 0 and x_eye != 0 and px != 0:
                Theta_True = np.abs(np.arctan(y_true_relative/x_true_relative))
                Theta_eye = np.abs(np.arctan(y_eye/x_eye))
                Theta_input = np.abs(np.arctan(py/px))

                Rad_True = np.hypot(x_true_relative,y_true_relative)
                Rad_eye = np.hypot(x_eye,y_eye)
                Rad_input = np.hypot(px , py)   
                
                Theta_Tx = (Theta_True/Theta_eye)*Theta_input
                Rad_Tx = (Rad_True/Rad_eye)*Rad_input

                out_x, out_y = (multiplier[0]*Rad_Tx*np.cos(Theta_Tx) + x_true_center, 
                                multiplier[1]*Rad_Tx*np.sin(Theta_Tx) + y_true_center )

                # print(out_x,out_y)

                if  (0 < out_x < SCREEN_WIDTH) and (0 < out_y < SCREEN_HEIGHT):
                    outputs.append([out_x,out_y])
                else:
                    outputs.append([0,0])
                    
            else:
                outputs.append([0,0])
        
        return outputs

    def save_calibration(self,folder_path):
        data = {
            "measurement_rate":self.measurement_rate,
            "calibration_pos":self.calibration_pos,
            "calibration_results":self.calibration_results,
            "calibration_true_values":self.calibration_true_values,
        }
        data = json.dumps(data)
        f = open(folder_path+"/calibration.json","w")
        f.write(data)
        f.close()
        return True
    
    def load_calibration(self,folder_path):
        f = open(folder_path+"/calibration.json","r")
        data = json.load(f)
        f.close()
        self.measurement_rate = data["measurement_rate"]
        self.calibration_pos = data["calibration_pos"]
        self.calibration_results = data["calibration_results"]
        self.calibration_true_values = data["calibration_true_values"]
        self.calibration_status = True
        return True
