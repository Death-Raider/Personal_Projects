from eye import Face_Eye_detector
import cv2
import numpy as np
from calibration import Calibrator

SCREEN_HEIGHT, SCREEN_WIDTH = 1080 , 1920

def input_stream_detection():
	FED = Face_Eye_detector()

	Cal = Calibrator()
	# Cal.load_calibration("TEST")
	save_cal = True

	cap = cv2.VideoCapture(0)
	ret,img = cap.read()
	cv2.namedWindow("img", cv2.WINDOW_NORMAL)
	cv2.setWindowProperty("img", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	while(ret):
		ret,img = cap.read()

		img = FED.resize_image(img,(SCREEN_WIDTH,SCREEN_HEIGHT))

		img_bgr,img_rgb,img_gray = FED.processing(img)

		faces = FED.getFacesCV(img_gray)
		if len(faces) < 1:
			print("didnt detect face")
			continue
		face_x,face_y,face_w,face_h = faces[0] # face position in image_gray [x,y,w,h]
		cv2.rectangle(img_bgr,(face_x,face_y),(int(face_x+face_w),int(face_y+face_h)),(0,0,255))

		face_rgb = img_rgb[face_y:face_y+face_h, face_x:face_x+face_w] 
		face_bgr = img_bgr[face_y:face_y+face_h, face_x:face_x+face_w]

		face_box = face_rgb.shape[:2]
		face_rgb = FED.resize_image(face_rgb,(300,300))
		face_bgr = FED.resize_image(face_bgr,(300,300))


		results = FED.mp_face_mesh.process(face_rgb)

		if not results.multi_face_landmarks:
			print("Didn't detect face")
			continue

		face_landmarks = results.multi_face_landmarks[0] # 0 - Only one face

		centers = FED.eyeball_pos(face_bgr,face_landmarks,True)
		# break
		calibration_status =	Cal.calibrate(centers,img_bgr,draw=True)

		if calibration_status:
			if save_cal:
				Cal.compress_calibrations()
				Cal.save_calibration("TEST")
				save_cal = not save_cal
				print("......saved......")

			screen_point = np.array(Cal.find_point_on_screen_linear(img_bgr,centers,face_box),dtype=int)
			r_max,l_max,r_min,l_min = Cal.get_bounding_eye()

			print("eye:",centers)
			print("screen:", screen_point[0][1],screen_point[0][0], screen_point[1][1],screen_point[1][0])

			Cal.draw_solid_circle(img_bgr,screen_point[0],r=4, color= (0,0,255))
			Cal.draw_solid_circle(img_bgr,screen_point[1],r=4, color= (0,255,0))
			cv2.rectangle(img_bgr,
							(int(r_min[0]*face_box[1]/300+face_x), int(r_min[1]*face_box[0]/300+face_y)),
							(int(r_max[0]*face_box[1]/300+face_x), int(r_max[1]*face_box[0]/300+face_y)),
							color=(0,0,255)
						)
			cv2.rectangle(img_bgr,
							(int(l_min[0]*face_box[1]/300+face_x), int(l_min[1]*face_box[0]/300+face_y)),
							(int(l_max[0]*face_box[1]/300+face_x), int(l_max[1]*face_box[0]/300+face_y)),
							color=(0,0,255)
						)
			for key in Cal.calibration_results.keys():
				for eye_index in range(2):
					x,y = Cal.calibration_results[key][eye_index] 
					x *= face_box[1]/300
					y *= face_box[0]/300
					cv2.circle(img_bgr,(int(x+face_x),int(y+face_y)),1,(255,255,255),5)

		for pos in centers:
			x,y = pos
			x = x * face_box[1]/300
			y = y * face_box[0]/300
			cv2.circle(img_bgr,(int(x+face_x),int(y+face_y)),1,(150,0,150),5)

		cv2.imshow('img',img_bgr)
		a = cv2.waitKey(1)
		if(a==ord('q')):
			break
	cap.release()
	cv2.destroyAllWindows()
	


input_stream_detection()