import os
import cv2
import numpy as np
import albumentations as A

# Paths
IMG_DIR = "test_frames/dataset/test/images/train"
LBL_DIR = "test_frames/dataset/test/labels/train"
OUT_IMG_DIR = "test_frames/dataset/test/images/train"
OUT_LBL_DIR = "test_frames/dataset/test/labels/train"
os.makedirs(OUT_IMG_DIR, exist_ok=True)
os.makedirs(OUT_LBL_DIR, exist_ok=True)

# Albumentations transform (with bbox support)
transform = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.GaussNoise(p=0.4),
    A.MotionBlur(p=0.3),
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=25, p=0.5),
    A.RandomScale(scale_limit=0.2, p=0.5),
    A.Perspective(p=0.3),
],
    bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])
)

def load_yolo_labels(label_path):
    bboxes = []
    class_labels = []
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            class_id = int(parts[0])
            bbox = list(map(float, parts[1:]))
            bboxes.append(bbox)
            class_labels.append(class_id)
    return bboxes, class_labels

def save_yolo_labels(label_path, bboxes, class_labels):
    with open(label_path, 'w') as f:
        for cls, bbox in zip(class_labels, bboxes):
            f.write(f"{cls} {' '.join(f'{x:.6f}' for x in bbox)}\n")

# Process all images
for filename in os.listdir(IMG_DIR):
    if not filename.endswith(".jpg") and not filename.endswith(".png"):
        continue

    name = os.path.splitext(filename)[0]
    img_path = os.path.join(IMG_DIR, filename)
    lbl_path = os.path.join(LBL_DIR, name + ".txt")

    if not os.path.exists(lbl_path):
        continue

    image = cv2.imread(img_path)
    height, width = image.shape[:2]

    bboxes, class_labels = load_yolo_labels(lbl_path)

    for i in range(8):  # Generate 5 variations per image
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)
        aug_img = transformed["image"]
        aug_bboxes = transformed["bboxes"]
        aug_labels = transformed["class_labels"]

        if len(aug_bboxes) == 0:
            continue  # Skip empty boxes

        new_img_name = f"{name}_aug{i}.jpg"
        new_lbl_name = f"{name}_aug{i}.txt"

        cv2.imwrite(os.path.join(OUT_IMG_DIR, new_img_name), aug_img)
        save_yolo_labels(os.path.join(OUT_LBL_DIR, new_lbl_name), aug_bboxes, aug_labels)
