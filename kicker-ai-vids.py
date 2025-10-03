from ultralytics import YOLO
import cv2
import numpy as np
import math
import urllib

cap = cv2.VideoCapture("videos/test.mp4")

frame_width, frame_height = 1920, 1080
move_threshold = 4

# Initialize heatmap (same size as frames)
heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
heatmap_mask = np.zeros((frame_height, frame_width), dtype=np.float32)

if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()
previous_loc = [None,None]
batch_size = 10
batch_frames = []
model = YOLO("best.pt")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    batch_frames.append(frame)

    if len(batch_frames) < batch_size:
        continue

    # Predict on batch
    results = model.predict(batch_frames, imgsz=1024, conf=0.5)

    # Loop over batch results
    for frame, result in zip(batch_frames, results):
        if result.boxes is None or len(result.boxes) == 0:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        names = result.names
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()
        detections_for_save = []

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.astype(int)
            cls = classes[i]
            
            conf = confidences[i]
            label = names[cls] if names else f"class {cls}"
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label_text = f"{label} {conf:.2f}"
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            if previous_loc[1] != None:
                dx = cx - previous_loc[0]
                dy = cy - previous_loc[1]
                distance = math.sqrt(dx**2 + dy**2)
                if distance < move_threshold:
                    continue    
            previous_loc = [cx,cy]  
            if cls == 1:  
                heatmap_mask[:] = 0
                cv2.circle(heatmap_mask, (cx, cy), 25, color=1, thickness=-1) 
                cv2.circle(heatmap_mask, (cx, cy), 15, color=2, thickness=-1)  # middle layer, value 2
                cv2.circle(heatmap_mask, (cx, cy), 5, color=3, thickness=-1)   # inner core, value 3
                
                
                # Add heat: increase intensity in the center (e.g., radius = 10–15)
                heatmap += heatmap_mask

                x_center = ((x1 + x2) / 2) / frame_width
                y_center = ((y1 + y2) / 2) / frame_height
                width = (x2 - x1) / frame_width
                height = (y2 - y1) / frame_height


        # Show frame
        cv2.imshow("Video Frame", frame)
        key = cv2.waitKey(30)
        if key == ord('q'):
            break
        elif key == ord("s"):
            img_name = f"frame_{save_count:05d}.jpg"
            label_name = f"frame_{save_count:05d}.txt"
            cv2.imwrite(f"test_frames/images/{img_name}", frame)

            with open(f"test_frames/labels/{label_name}", "w") as f:
                for line in detections_for_save:
                    f.write(line + "\n")

            print(f"✅ Saved frame {img_name} and labels.")
            save_count += 1
    # Clear batch for next round
    batch_frames.clear()
    heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_uint8 = heatmap_norm.astype(np.uint8)
    heatmap_blurred = cv2.GaussianBlur(heatmap_uint8, (25, 25), 0)
    colored_heatmap = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)
    cv2.imshow("Ball Heatmap", colored_heatmap)


heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
heatmap_uint8 = heatmap_norm.astype(np.uint8)
heatmap_blurred = cv2.GaussianBlur(heatmap_uint8, (25, 25), 0)
colored_heatmap = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)
cv2.imshow("Ball Heatmap", colored_heatmap)
# Cleanup
cv2.waitKey(0)


cap.release()
cv2.destroyAllWindows()
