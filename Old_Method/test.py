import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
from eye import Face_Eye_detector
import time
from calibration import Calibrator

# test to compute the average position of the eye form the calibration data
def test1():

    f=open("TEST/calibration.json","r")
    data = json.load(f)
    f.close

    calibration_data = data["calibration_results"]
    eye_box_size = data["calibration_eye_box"]
    out_data = dict.fromkeys(calibration_data.keys(),np.zeros((2,2)))
    i = 1
    right_eye = np.zeros((40,40))
    left_eye = np.zeros((40,40))
    for k in calibration_data.keys():
        calibration_data[k] = np.array(calibration_data[k],dtype=int)
        out_data[k] = calibration_data[k]#.mean(axis=0).astype(int)

        # eye_box_size[k] = np.array(eye_box_size[k])
        # eye_box_size[k] = calibration_data[k].mean(axis=0)#.astype(int)

        print(k,out_data[k].tolist())
        # print(eye_box_size[k].tolist())

        
        right_eye[out_data[k][0][1],out_data[k][0][0]] = 255*i/6
        left_eye[out_data[k][1][1],out_data[k][1][0]] = 255*i/6
        i+=1

    cv2.imwrite('Images/color_img_R'+'.jpg', right_eye)
    cv2.imwrite('Images/color_img_L'+'.jpg', left_eye)
    time.sleep(0.1)

#test to use the shape predictor from dlib
def test2():

    import dlib
    from imutils import face_utils

    R_eye = list(face_utils.FACIAL_LANDMARKS_IDXS.items())[4]
    L_eye = list(face_utils.FACIAL_LANDMARKS_IDXS.items())[5]
    face_landmarks = dlib.shape_predictor("Models/shape_predictor_68_face_landmarks.dat")

    #facial points using face_landmark_dat file  
    def dlib_detector(frame,face,draw=True):

        (x,y,w,h) = face[0]
        dlibRect = dlib.rectangle(x, y, w+x, h+y)

        shape_out = face_landmarks(frame, dlibRect)
        shape_out = face_utils.shape_to_np(shape_out)

        R_eye_points = shape_out[R_eye[1][0]:R_eye[1][1]]
        L_eye_points = shape_out[L_eye[1][0]:L_eye[1][1]]
        if draw :
            for (ptsx,ptsy) in R_eye_points:
                cv2.circle(frame, (ptsx, ptsy), 1, (255, 255, 255), -1)
            for (ptsx,ptsy) in L_eye_points:
                cv2.circle(frame, (ptsx, ptsy), 1, (255, 255, 255), -1)
        return R_eye_points,L_eye_points

    def extract_features(img,FED,draw=False):
        roi_face_clr = np.zeros((80,80,3)).tolist()
        roi_face = np.zeros((80, 80, 1)).tolist()
        roi_eye_clr = np.zeros((2,50,50,3)).tolist()
        roi_eye = np.ones((2,50,50)).tolist()

        eyes = np.zeros((2,4)).tolist()

        processed_img = FED.process_RGB_img(img)
        faces = FED.getFaces(processed_img)
        face_counter = 0
        for (x,y,w,h) in faces:
            if draw: 
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2) # draw the face bb
            roi_face = processed_img[y:y+h,x:x+w]
            roi_face_clr = img[y:y+h,x:x+w]

            eyes = FED.getEyes_individual(roi_face)
            eye_counter = 0

            for (ex,ey,ew,eh) in eyes:
                if draw:
                    img = cv2.rectangle(img,(ex+x,ey+y),(ex+x+ew,ey+y+eh),(0,0,255),2) # draw the eye bb
                #dynamically allocated size
                if eye_counter < 2:
                    roi_eye[eye_counter] = processed_img[y+ey:ey+y+eh, x+ex:x+ex+ew]
                    roi_eye_clr[eye_counter] = img[y+ey:ey+y+eh, x+ex:x+ex+ew]
                eye_counter += 1
            face_counter+=1
        
        return (roi_face_clr, roi_face, roi_eye_clr, roi_eye , faces , eyes)

    FED = Face_Eye_detector()
    cap = cv2.VideoCapture(0)
    ret,img = cap.read()

    while(ret):
        ret,img = cap.read()
        # img = FED.process_RGB_img(img)
        # faces = FED.getFaces(img) # face  = [(x,y,w,h), ...]
        (roi_face_clr, roi_face, roi_eye_clr, roi_eye ,faces, eye_pos) = extract_features(img,FED,True)

        if len(faces) != 1:
            continue

        eye_count = 0
        for eye in roi_eye:
            eye = np.array(eye)
            eye = eye.reshape([*eye.shape,1]).astype(np.uint8)

            circles = cv2.HoughCircles(eye,
                                        cv2.HOUGH_GRADIENT,
                                        dp = 1,minDist = 5,  param1=250,param2=10,minRadius=1,maxRadius=-1
                                       )
            print(circles)
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0,:1]:
                    # draw the outer circle
                    cv2.circle(img,(i[0] + eye_pos[eye_count][0] + faces[0][0],i[1] + eye_pos[eye_count][1] + faces[0][1]),
                               1,(0,255,0),1)
                    # draw the center of the circle
                    # cv2.circle(img,(i[0]+eye_pos[eye_count][0],i[1]+eye_pos[eye_count][1]),2,(0,0,255),3)

            eye_count+=1
            
        cv2.imshow('img',img)
        a = cv2.waitKey(1)
        if(a==ord('q')):
            break

# test to use the pupil detector cv class to increase stability
def test3():

    image = cv2.imread('test_img/face_img.png')
    eye = cv2.imread('test_img/eye2.png')
    image =  cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eye =  cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)

    # import dlib
    # from imutils import face_utils
    # R_eye = list(face_utils.FACIAL_LANDMARKS_IDXS.items())[4]
    # L_eye = list(face_utils.FACIAL_LANDMARKS_IDXS.items())[5]
    # face_landmarks = dlib.shape_predictor("Models/shape_predictor_68_face_landmarks.dat")
    # h,w = image.shape
    # dlibRect = dlib.rectangle(0, 0, w+0, h+0)
    # shape_out = face_landmarks(image, dlibRect)
    # shape_out = face_utils.shape_to_np(shape_out)
    # R_eye_points = shape_out[R_eye[1][0]:R_eye[1][1]]
    # L_eye_points = shape_out[L_eye[1][0]:L_eye[1][1]]
    # for (ptsx,ptsy) in R_eye_points:
    #     cv2.circle(image, (ptsx, ptsy), 1, (255, 255, 255), -1)
    # for (ptsx,ptsy) in L_eye_points:
    #     cv2.circle(image, (ptsx, ptsy), 1, (255, 255, 255), -1)
    # print(w,h,R_eye_points,L_eye_points)

# show the eye position locations
def test4():
    
    with open("Images/eye_track_L.txt","r") as f:
        data = f.read()
    dataL = np.array(eval(data))
    with open("Images/eye_track_R.txt","r") as f:
        data = f.read()
    dataR = np.array(eval(data))

    eye_locations_L = np.where(dataL > 0)
    eye_locations_L = [[x,y] for (y,x) in zip(*eye_locations_L)]
    for i,(x,y) in enumerate(eye_locations_L):
        eye_locations_L[i].append(int(dataL[y][x]))

    eye_locations_R = np.where(dataR > 0)
    eye_locations_R = [[x,y] for (y,x) in zip(*eye_locations_R)]
    for i,(x,y) in enumerate(eye_locations_R):
        eye_locations_R[i].append(int(dataR[y][x]))

    print(np.array(eye_locations_R))
    print(np.array(eye_locations_L))
    

    # plt.figure()
    # plt.imshow(dataL*255/dataL.max())
    # plt.show()


gray_matrix = 255*np.arange(0,300*300).reshape((300,300))/(300*300)
out_gray_matrix = gray_matrix.copy()

plt.figure()
plt.imshow(gray_matrix)
plt.show()

Cal = Calibrator()
Cal.load_calibration("TEST")

eye_pos = np.arange(0,300*300,dtype=np.uint8)

every_pos = np.array([[[x,y],[0,0]] for x in range(300) for y in range(300)])
print(every_pos)
clone = gray_matrix.copy().reshape((300,300,1))

for i in range(len(every_pos)):
    pos = every_pos[i]
    out = Cal.find_point_on_screen_polar(clone,pos)
    x,y = out[0]
    x0,y0 = pos[0]
    try:
        out_gray_matrix[y0,x0] = gray_matrix[int(y),int(x)]
    except:
        print(pos[0],y,x)
plt.figure()
plt.imshow(out_gray_matrix)
plt.show()