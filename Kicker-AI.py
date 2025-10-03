from ultralytics import YOLO
import cv2
import numpy as np
import urllib
#url = "https://ultralytics.com/images/bus.jpg"
#req = urllib.request.urlopen(url)
#arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
#img = cv2.imdecode(arr, -1)
img = cv2.imread("images/kicker_1.jpg")


model = YOLO("runs/detect/train2/weights/best.pt")
results = model.train(data="table images/table_dataset.yaml", epochs = 10, imgsz = 1024, device = -1, lr0 = 0.1)

results = model.predict(img,imgsz=1024)
img = cv2.resize(img,(640,480))
for result in results:
    if result.boxes is None:
        print("no results found")
        continue
    masks = result.masks.data
    boxes = result.boxes.xyxy.cpu().numpy()  # (N, 4)
    names = result.names  # class ID to label mapping
    classes = result.boxes.cls.cpu().numpy().astype(int)  # class indices

    for i, mask in enumerate(masks):
        color = np.random.randint(0, 255, size=3).tolist()

        # Resize and apply mask
        color_mask = np.zeros_like(img)
        mask_np = mask.cpu().numpy()
        color_mask[mask_np.astype(bool)] = color
        img = cv2.addWeighted(img, 1.0, color_mask, 0.5, 0)

        # Draw bounding box and label
        x1, y1, x2, y2 = boxes[i].astype(int)
        cls = classes[i]
        label = names[cls] if names else f"class {cls}"
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

# Save and display
img = cv2.resize(img,(640,480))
cv2.imshow("Yolov11 Segmentation",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("yolo_segmentation_result.jpg", img)