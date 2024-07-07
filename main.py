from datetime import date, datetime
import time
import os
import sys
import shutil
import mediapipe 
import cv2
import mediapipe as mp

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

def landmark_in_bound(results, image_width, image_height):
	global point_1, point_2

	try:
		_, landmarks = results.pose_landmarks.ListFields()[-1]

		x1, y1 = point_1
		x2, y2 = point_2
		for landmark in landmarks:
			if landmark.visibility >= 0.75:
				x, y = int(landmark.x * image_width), int(landmark.y * image_height)
				if x >= x1 and x <= x2 and y >= y1 and y <= y2:	
					return True
	
	except AttributeError as E:
		print("Edge Case, ghost points")

	except Exception as E:
		print(E)

	return False

def run_time():
	capture = cv2.VideoCapture(0)
	with mediapipe.solutions.pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5) as pose:
		while capture.isOpened():

			# Read from the capture object and generate pose results
			ret, image = capture.read()
			image_height, image_width, _ = image.shape
		
			# Verify on_mouse_press has triggered for both points, properly forming bounding box
			if point_1 and point_2:
				x1, y1 = point_1
				x2, y2 = point_2
				subframe = image[y1:y2, x1:x2]
				results = pose.process(subframe)
				cv2.imshow("Subframe", subframe)

				# If in bounds draw green rectangle and try to save frame.
				if landmark_in_bound(results, image_width, image_height):
					cv2.rectangle(image, point_1, point_2, (0,255,0), 2)
					try:
						time_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
						os.mkdir(f"images/{time_stamp}") 
						cv2.imwrite(f"images/{time_stamp}/{time_stamp}.png", image)
						shutil.make_archive(f"images/{time_stamp}", "zip", f"images/{time_stamp}")

						shutil.rmtree(f"images/{time_stamp}")

					except Exception as E: print(f"Error... {E}")

				else:
					cv2.rectangle(image, point_1, point_2, (0,0,255), 2)

			cv2.imshow("Project", image)
			cv2.setMouseCallback("Project", on_mouse_press)
		
			if cv2.waitKey(25) & 0xFF == ord("q"):
				break

	capture.release()
	cv2.destroyWindow("Project")

def process_zips():
	pass

if __name__ == "__main__":

	if len(sys.argv) == 2:

		if sys.argv[1] == "-c":
			run_time()
		
		elif sys.argv[1] == "-p":
			process_zips()
		
		else:
			print(f"Error... use -c for camera instance or -p for process zips instance.")