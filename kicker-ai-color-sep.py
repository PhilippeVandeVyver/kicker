import cv2
import numpy as np
from ultralytics import YOLO
import urllib

def isolate_red_object(image):
    # Load image
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range (two ranges needed due to hue wrap-around)
    lower_ball = np.array([7, 80, 9])
    upper_ball = np.array([10, 160, 255])

    # Create two masks and combine them
    red_mask = cv2.inRange(hsv, lower_ball, upper_ball)
    

    # Optional: Clean noise with morphological operations
    kernel = np.ones((5,5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

    # Apply the mask to the original image
    result = cv2.bitwise_and(image, image, mask=red_mask)
    return result, red_mask
    # Show results
    
    cv2.destroyAllWindows()


cap = cv2.VideoCapture("videos/vid_4.mp4")

if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()


while True:
    ret, frame = cap.read()
    
    if not ret:
        print("End of video or error.")
        break
    result, red_mask = isolate_red_object(frame)
    print(frame[0,0])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("Original", frame)
    cv2.imshow("Red Mask", red_mask)
    cv2.imshow("Isolated Red", result)
    key = cv2.waitKey(0)

    # Optional: Quit on specific key (e.g., 'q')
    if key == ord('q'):
        print("Exiting...")
        break
# Cleanup
cap.release()
cv2.destroyAllWindows()
