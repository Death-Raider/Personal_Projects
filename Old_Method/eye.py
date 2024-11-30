
import cv2
import numpy as np
import mediapipe as mp

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

LEFT_EYE = [257,253,463,359] # top bottom right left
RIGHT_EYE = [27,23,130,243] # top bottom right left

FACE_BOX = [[10,234],[152,454]] #x1y1 x2y2

class Face_Eye_detector:
	def __init__(self):
		#Initializing the face and eye cascade classifiers from xml files
		#  wget https://github.com/kipr/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml -o haarcascade_frontalface_default.xml
		#  wget https://github.com/kipr/opencv/blob/master/data/haarcascades/haarcascade_eye_tree_eyeglasses.xml -o haarcascade_eye_tree_eyeglasses.xml

		self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
		self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')
		self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
																max_num_faces=1,
																min_detection_confidence=0.5,
																min_tracking_confidence=0.5,
																refine_landmarks=True
															)

	def getFacesCV(self,frame,size=(400,400)): # assumes frame is grey scaled
		return self.face_cascade.detectMultiScale(frame,1.3,5)
	
	def getFacesMediapipe(self,frame,face_landmarks):
		frame_height = frame.shape[0]
		frame_width = frame.shape[1]
		mesh_points = np.array([np.multiply([p.x,p.y],[frame_width,frame_height]) for p in face_landmarks.landmark])
		[[top_x, top_y] , [left_x, left_y]] = mesh_points[FACE_BOX[0]].astype(int) # [top_x top_y] , [left_x left_y]
		[[bottom_x, bottom_y] , [right_x, right_y]] = mesh_points[FACE_BOX[1]].astype(int) # [bottom_x bottom_y] , [right_x right_y]
		
		return [[left_x,top_y],[right_x,bottom_y]]

	def getEyes_individual(self,frame,size=(50,50)): # assumes frame is just the face
		return self.eye_cascade.detectMultiScale(frame,1.3,5,maxSize=size)
	
	def getEyes_strip(self,eyes): # assumes eyes is a numpy array [eye1,eye2] where eye1/2 = [x,y,w,h]
		if len(eyes_individual) == 2:
			eyes_individual = np.apply_along_axis(self.xywh_to_x1y1x2y2,1,eyes_individual)
			eyes_individual = np.concatenate((eyes_individual[0][:2],eyes_individual[1][2:])).flatten()
		else: 
			eyes_individual = ()
		return eyes_individual

	def processing(self,frame):
		frame = cv2.flip(frame,1)
		bgr_frame = frame
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		return bgr_frame,rgb_frame,gray_frame
	
	def resize_image(self,frame,shape): # shape=[x,y]
		return cv2.resize(frame,shape)

	def eyeball_pos(self,frame,face_landmarks,draw=True):
               
		frame_height = frame.shape[0]
		frame_width = frame.shape[1]
		mesh_points=np.array([np.multiply([p.x,p.y],[frame_width,frame_height]) for p in face_landmarks.landmark])

		(l_x,l_y), l_radius = cv2.minEnclosingCircle(np.int32(mesh_points[LEFT_IRIS]))
		(r_x,r_y), r_radius = cv2.minEnclosingCircle(np.int32(mesh_points[RIGHT_IRIS]))
		# r_eye_box = np.int32(mesh_points[RIGHT_EYE]) # (4,2) eye_positions, coordinates
		# l_eye_box = np.int32(mesh_points[LEFT_EYE]) # (4,2) eye_positions, coordinates

		# r_eye_box = [r_eye_box[2][0], r_eye_box[0][1], r_eye_box[3][0]-r_eye_box[2][0], r_eye_box[1][1]-r_eye_box[0][1]]
		# l_eye_box = [l_eye_box[2][0], l_eye_box[0][1], l_eye_box[3][0]-l_eye_box[2][0], l_eye_box[1][1]-l_eye_box[0][1]]

		center_left = [int(l_x),int(l_y)]
		center_right = [int(r_x),int(r_y)]
		
		# r_x * r_eye_box[2]/frame_width
		# r_y * r_eye_box[3]/frame_height

		# l_x * r_eye_box[2]/frame_width
		# l_y * r_eye_box[3]/frame_height

		if draw:
			# cv2.rectangle(frame,r_eye_box[:2],(r_eye_box[0]+r_eye_box[2],r_eye_box[1]+r_eye_box[3]),color=(0,0,255))
			# cv2.rectangle(frame,l_eye_box[:2],(l_eye_box[0]+l_eye_box[2],l_eye_box[1]+l_eye_box[3]),color=(0,0,255))
			cv2.circle(frame,center=center_left,radius=1,color=(255,0,255),thickness=2)
			cv2.circle(frame,center=center_right,radius=1,color=(255,0,255),thickness=2)

		return [[r_x,r_y],[l_x,l_y]] # , (r_eye_box,l_eye_box)
	
