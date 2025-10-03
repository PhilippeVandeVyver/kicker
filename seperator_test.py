from PIL import Image
import requests
from transformers import SamModel, SamProcessor, pipeline
import matplotlib.pyplot as plt
import numpy as np

""" #this generates a mask inside the input points/ specified area
model = SamModel.from_pretrained("facebook/sam-vit-base")
processor = SamProcessor.from_pretrained("facebook/sam-vit-base")

img_url = "https://huggingface.co/ybelkada/segment-anything/resolve/main/assets/car.png"
raw_image = Image.open("table images/images/train/table_1.jpg").convert("RGB")
input_points = [[[450, 600]]] # 2D localization of a window
inputs = processor(raw_image, input_points=input_points, return_tensors="pt").to("cuda")
outputs = model(**inputs)
masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu())
scores = outputs.iou_scores
"""

generator =  pipeline("mask-generation", device = 0, points_per_batch = 256)
image_url = "table images/images/train/table_1.jpg"
outputs = generator(image_url, points_per_batch = 256)



def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    
raw_image = Image.open(image_url)
plt.imshow(np.array(raw_image))
ax = plt.gca()
for mask in outputs["masks"]:
    show_mask(mask, ax=ax, random_color=True)
plt.axis("off")
plt.show()

