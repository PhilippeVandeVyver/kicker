from __future__ import print_function
import cv2 as cv
import numpy as np
import os
# LOW_H 6
# LOW S
# LOW_V
# HIGH_H = 16
# HIGH_S
# HIGH_V =
max_value = 255
max_value_H = 360//2
low_H = 5
low_S = 81
low_V = 101
high_H = 17
high_S = 249
high_V = 244
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'
"""
image_dir = "test_frames/dataset/dataset/images"
label_dir = "test_frames/dataset/labels"

image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
"""
def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H-1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)
def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H+1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)
def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S-1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)
def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S+1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)
def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V-1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)
def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V+1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
cv.createTrackbar(low_H_name, window_detection_name , low_H, max_value_H, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name , high_H, max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name , low_S, max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name , high_S, max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name , low_V, max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name , high_V, max_value, on_high_V_thresh_trackbar)
"""
for img_file in image_files:
    image_path = os.path.join(image_dir, img_file)
    label_path = os.path.join(label_dir, os.path.splitext(img_file)[0] + ".txt")

    frame = cv.imread(image_path)
"""

cap = cv.VideoCapture("videos/test.mp4")
while True:
        
    ret, frame = cap.read()
     
    if frame is None:
        continue
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (8, 8))
    cleaned_mask = cv.morphologyEx(frame_threshold, cv.MORPH_OPEN, kernel)
    cleaned_mask = cv.morphologyEx(cleaned_mask, cv.MORPH_CLOSE, kernel)
    best_contour = None
    best_area = 0
    contours, _ = cv.findContours(cleaned_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv.contourArea(cnt)
        perimeter = cv.arcLength(cnt, True)

        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter ** 2)

        if area > 100 and 0.7 < circularity <= 1.2:
            if area > best_area:
                best_area = area
                best_contour = cnt
    if best_contour is not None:
        # Draw best contour
        cv.drawContours(frame, [best_contour], -1, (0, 255, 0), 2)

        # Optional: bounding box
        x, y, w, h = cv.boundingRect(best_contour)
        cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # That's likely the ball
    cv.imshow(window_capture_name, frame)
    cv.imshow(window_detection_name, cleaned_mask)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break
    elif key == ord('s') and best_contour is not None:
        h_img, w_img = frame.shape[:2]
        x_center = (x + w / 2) / w_img
        y_center = (y + h / 2) / h_img
        width = w / w_img
        height = h / h_img

        ball_class_id =  1 # You can change this to match your dataset's class ID for the ball

        line = f"{ball_class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        with open(label_path, "a") as f:
            f.write(line)
        print(f"✅ Added ball label to {label_path}")

cv.destroyAllWindows()