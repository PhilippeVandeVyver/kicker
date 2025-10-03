import os
import random
import shutil

# Paths
base_path = "test_frames/dataset/test"
images_path = "test_frames/dataset/test/images"
labels_path = "test_frames/dataset/test/labels"

train_ratio = 0.8  # 80% training, 20% validation

# Output directories
for split in ['train', 'val']:
    os.makedirs(os.path.join(base_path, 'images', split), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'labels', split), exist_ok=True)

# Get list of image files
image_files = [f for f in os.listdir(images_path) if f.endswith(('.jpg', '.png'))]
random.shuffle(image_files)

# Split
split_index = int(len(image_files) * train_ratio)
train_files = image_files[:split_index]
val_files = image_files[split_index:]

def move_files(file_list, split):
    for image_file in file_list:
        label_file = image_file.rsplit('.', 1)[0] + '.txt'

        src_img = os.path.join(images_path, image_file)
        src_lbl = os.path.join(labels_path, label_file)

        dst_img = os.path.join(base_path, 'images', split, image_file)
        dst_lbl = os.path.join(base_path, 'labels', split, label_file)

        if os.path.exists(src_img) and os.path.exists(src_lbl):
            shutil.copy2(src_img, dst_img)
            shutil.copy2(src_lbl, dst_lbl)

move_files(train_files, 'train')
move_files(val_files, 'val')

print(f"✅ Split complete: {len(train_files)} train, {len(val_files)} val")
