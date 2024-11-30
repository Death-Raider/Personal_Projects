import cv2
import mediapipe as mp
import numpy as np
import time


LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374

blink_count = 0
last_blink_time = 0
double_blink_time_threshold = 2.0 


 

def blink_detection(frame,face_landmarks):
    global blink_count, last_blink_time
    
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    
    ##LEFT TOP
    left_top_landmark = face_landmarks.landmark[LEFT_EYE_TOP]
    left_top_centre = np.array(np.multiply([left_top_landmark.x,left_top_landmark.y],[frame_width,frame_height]),dtype=np.int32)
    cv2.circle(frame,center=left_top_centre,radius=2,color=(0,255,255),thickness=1)
    
    ##LEFT BOTTOM
    left_bottom_landmark = face_landmarks.landmark[LEFT_EYE_BOTTOM]
    left_bottom_centre = np.array(np.multiply([left_bottom_landmark.x,left_bottom_landmark.y],[frame_width,frame_height]),dtype=np.int32)
    cv2.circle(frame,center=left_bottom_centre,radius=2,color=(0,255,255),thickness=1)
    
    ##RIGHT TOP
    right_top_landmark = face_landmarks.landmark[RIGHT_EYE_TOP]
    right_top_centre = np.array(np.multiply([right_top_landmark.x,right_top_landmark.y],[frame_width,frame_height]),dtype=np.int32)
    cv2.circle(frame,center=right_top_centre,radius=2,color=(0,255,255),thickness=1)
    
    ##RIGHT BOTTOM
    right_bottom_landmark = face_landmarks.landmark[RIGHT_EYE_BOTTOM]
    right_bottom_centre = np.array(np.multiply([right_bottom_landmark.x,right_bottom_landmark.y],[frame_width,frame_height]),dtype=np.int32)
    cv2.circle(frame,center=right_bottom_centre,radius=2,color=(0,255,255),thickness=1)
    
    
    if (left_bottom_landmark.y - left_top_landmark.y ) <0.004 and (right_bottom_landmark.y - right_top_landmark.y )<0.004:
        current_time = time.time()

        if current_time - last_blink_time < double_blink_time_threshold:
            blink_count += 1
            print("Double blink detected")

        last_blink_time = current_time

        cv2.putText(frame, "Blink Detected", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

def eyeball_plot(frame,face_landmarks):
               
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        mesh_points=np.array([np.multiply([p.x,p.y],[frame_width,frame_height]) for p in face_landmarks.landmark])
        
        (l_x,l_y), l_radius = cv2.minEnclosingCircle(np.int32(mesh_points[LEFT_IRIS]))
        (r_x,r_y), r_radius = cv2.minEnclosingCircle(np.int32(mesh_points[RIGHT_IRIS]))
        
        #cv2.polylines(frame, np.int32([mesh_points[LEFT_EYE]]),True,(0,255,0), 1, cv2.LINE_AA)
        #cv2.polylines(frame, np.int32([mesh_points[RIGHT_EYE]]),True,(0,255,0), 1, cv2.LINE_AA) 
        
        center_left = np.array([l_x,l_y],dtype=np.int32)
        center_right = np.array([r_x,r_y],dtype=np.int32)
        cv2.circle(frame,center=center_left,radius=1,color=(255,0,255),thickness=2) #int(l_radius)
        cv2.circle(frame,center=center_right,radius=1,color=(255,0,255),thickness=2) #int(r_radius)
        
        return [[r_x,r_y],[l_x,l_y]]
        
def main():
    
    cap = cv2.VideoCapture(0)

    mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        refine_landmarks=True)

    while True:
        _,frame = cap.read()     #_ - 0 - No frame detected, 1 - Frame detected
        frame = cv2.flip(frame,1)
        rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        
        results = mp_face_mesh.process(rgb_frame)
        
        if (results.multi_face_landmarks):
            face_landmarks = results.multi_face_landmarks[0] # 0 - Only one face, so getting the landmarks only for the Zeroth index
            eyeball_plot(frame,face_landmarks)
            blink_detection(frame,face_landmarks)
                
        cv2.imshow('HumanoidX - Iris Movement Detection',frame)
        
        if cv2.waitKey(1)  & 0xFF == "27":
            break
        
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()