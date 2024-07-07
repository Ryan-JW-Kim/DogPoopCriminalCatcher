from datetime import date, datetime
import time
import os
import sys
import mediapipe 
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

pose = mediapipe.solutions.pose
capture = cv2.VideoCapture(0)
point_1, point_2 = None, None

def on_mouse_press(event, x, y, flags, param):
	global point_1, point_2
	if event == cv2.EVENT_LBUTTONDOWN: point_1 = (x, y)
	elif event == cv2.EVENT_LBUTTONUP: point_2 = (x, y)
	elif flags == 1: point_2 = (x, y)

	if point_1 and point_2:
		(x1, y1), (x2, y2) = point_1, point_2
		_x1, _x2 = min(x1, x2), max(x1, x2)
		_y1, _y2 = min(y1, y2), max(y1, y2)
		point_1, point_2 = (_x1, _y1), (_x2, _y2)
		# print(f"Adjusted {point_1}  ++  {point_2}")

draw_poses = False

with pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5) as pose:
	while capture.isOpened():

		ret, image = capture.read()
		image_height, image_width, _ = image.shape

		# image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
		results = pose.process(image)
	
		if point_1 and point_2:
			cv2.rectangle(image, point_1, point_2, (0,255,0), 3)


			try:
				_, landmarks = results.pose_landmarks.ListFields()[-1]

				x1, y1 = point_1
				x2, y2 = point_2
				for landmark in landmarks:
					if landmark.visibility >= 0.75:
						x, y = int(landmark.x * image_width), int(landmark.y * image_height)
						print(landmark)
						if x >= x1 and x <= x2 and y >= y1 and y <= y2:	
							cv2.rectangle(image, (x, y), (x+2, y+2), (0,0,255), 3)

			except AttributeError as E:
				print("Edge Case, ghost points")

			except Exception as E:
				print(E)

		cv2.imshow("Project", image)
		cv2.setMouseCallback("Project", on_mouse_press)
	
		if cv2.waitKey(25) & 0xFF == ord("q"):
			break

capture.release()
cv2.destroyWindow("Project")