from ultralytics import YOLO
import cv2
import numpy as np
import math
import os

image_folder = "test_frames"  # Change to your folder name
frame_width, frame_height = 1920, 1080
move_threshold = 4
batch_size = 10
img_size = 1024
model_path = "runs/detect/train11/weights/best.pt"

os.makedirs("test_frames/dataset/images", exist_ok=True)
os.makedirs("test_frames/dataset/labels", exist_ok=True)
save_count = 0
# Initialize heatmap (same size as frames)
heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
heatmap_mask = np.zeros((frame_height, frame_width), dtype=np.float32)



previous_loc = [None, None]
batch_frames = []
image_paths = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
print(image_paths)
index = 0
model = YOLO("runs/detect/train11/weights/best.pt")
while index < len(image_paths):
    img_path = image_paths[index]
    print(img_path)
    img = cv2.imread(img_path)
    frame = img.copy()
    index += 1
    if frame is None:
        continue
    # Predict on batch
    results = model.predict(frame, imgsz=1024, conf=0.6)
    for result in results:
        if result.boxes is None or len(result.boxes) == 0:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        names = result.names
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()
        detections_for_save = []

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.astype(int)
            cls = classes[0]
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
                print("distance = " + str(distance))
                if distance < move_threshold:
                    continue    
            previous_loc = [cx,cy]    
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
            detections_for_save.append(f"{cls} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")


        # Show frame
        cv2.imshow("Video Frame", frame)
        key = cv2.waitKey(30)
        if key == ord('q'):
            break
        elif key != ord("s"):
            img_name = f"frame_{save_count:05d}.jpg"
            label_name = f"frame_{save_count:05d}.txt"
            cv2.imwrite(f"test_frames/dataset/images/{img_name}", img)

            with open(f"test_frames/dataset/labels/{label_name}", "w") as f:
                for line in detections_for_save:
                    f.write(line + "\n")

            print(f"✅ Saved frame {img_name} and labels.")
            save_count += 1
    # Clear batch for next round
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
cv2.destroyAllWindows()
