import cv2
import numpy as np

def show_pixel_info(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        bgr = image[y, x]
        hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        print(f"Position: ({x}, {y})")
        print(f"BGR: {bgr}")
        print(f"HSV: {hsv}")
        print("-" * 30)

# Load image
image = cv2.imread("output_frames/vid4_00012.jpg")
cv2.namedWindow("Click on Ball")
cv2.setMouseCallback("Click on Ball", show_pixel_info)

while True:
    cv2.imshow("Click on Ball", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press 'q' to quit
        break

cv2.destroyAllWindows()