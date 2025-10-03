import os
import shutil

# Paths
source_folder = "test_frames/dataset/test"
labels_folder = os.path.join(source_folder, "labels")
images_folder = os.path.join(source_folder, "images")

# Create folders if not exist
os.makedirs(labels_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)

# Move files
for filename in os.listdir(source_folder):
    filepath = os.path.join(source_folder, filename)
    if filename.endswith(".txt"):
        # Skip classes.txt if present
        if filename.lower() != "classes.txt":
            shutil.move(filepath, os.path.join(labels_folder, filename))
    elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
        shutil.move(filepath, os.path.join(images_folder, filename))

print("✅ Files sorted into labels/ and images/ folders.")