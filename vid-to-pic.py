import cv2
import os

def video_to_images(video_path, output_dir, prefix='frame', image_format='jpg'):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    frames= 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if frames % 15 == 0:
            if not ret:
                break  # No more frames

            # Generate image filename
            filename = os.path.join(output_dir, f"{prefix}_{frame_count:05d}.{image_format}")

            # Save the frame as an image
            cv2.imwrite(filename, frame)

            frame_count += 1
        frames += 1
    cap.release()
    print(f"Done! Extracted {frame_count} frames to '{output_dir}'")

# Example usage
if __name__ == "__main__":
    video_path = "videos/test.mp4"        # Path to your video
    output_dir = "test_frames"          # Output directory
    video_to_images(video_path, output_dir,prefix="test")
