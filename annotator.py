import cv2 as cv
import numpy as np
import os

os.makedirs("images", exist_ok=True)
os.makedirs("labels", exist_ok=True)

low_H = 5
low_S = 120
low_V = 30
high_H = 12
high_S = 230
high_V = 252


cap = cv.VideoCapture("videos/vid_3.mp4")
frame_idx = 0
y_threshold = 103  # Skip detections above this y-coordinate
class_id = 0 

while True:
    ret, frame = cap.read()
    if frame is None:
        break
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
            x, y, w, h = cv.boundingRect(cnt)
            if y >= y_threshold and area > best_area:
                best_area = area
                best_contour = cnt
    if best_contour is not None:
        x, y, w, h = cv.boundingRect(best_contour)
        img_h, img_w = frame.shape[:2]

        # Normalize for YOLO format
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        width = w / img_w
        height = h / img_h

        # Save image
        image_path = f"images/frame3_{frame_idx:04}.jpg"
        label_path = f"labels/frame3_{frame_idx:04}.txt"
        cv.imwrite(image_path, frame)

        # Save annotation
        with open(label_path, "w") as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"Saved frame {frame_idx:04} with ball at y={y}")

    else:
        print(f"Skipped frame {frame_idx:04} (no valid ball found or too high)")

    frame_idx += 1

cap.release()