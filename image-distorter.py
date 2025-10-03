import cv2
import os
import numpy as np
import shutil

# Paths
input_img_dir = "table images/images/"
input_lbl_dir = "table images/labels/"
output_img_dir = "table images/aug_images/"
output_lbl_dir = "table images/aug_labels/"

# Create output folders
os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_lbl_dir, exist_ok=True)

def adjust_brightness(img, factor):
    return cv2.convertScaleAbs(img, alpha=factor, beta=0)

def add_blur(img, ksize=5):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)

# Loop through images
for filename in os.listdir(input_img_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(input_img_dir, filename)
        label_path = os.path.join(input_lbl_dir, filename.rsplit(".", 1)[0] + ".txt")

        image = cv2.imread(img_path)

        # --- Apply transformations ---
        factors = [0.3,0.7,0.9,1.4,1.6]
        for fact in factors:
            bright = adjust_brightness(image, factor=fact)
            blurred = add_blur(bright)

        # Save image
            out_img_name = "aug_" + filename.rsplit(".", 1)[0] + str(int(fact*10)) + "." + filename.rsplit(".", 1)[1]
            out_img_path = os.path.join(output_img_dir, out_img_name)
            cv2.imwrite(out_img_path, blurred)

            # Copy label file unchanged
            out_label_path = os.path.join(output_lbl_dir, "aug_" + filename.rsplit(".", 1)[0] + str(int(fact*10))+ ".txt")
            shutil.copy(label_path, out_label_path)
