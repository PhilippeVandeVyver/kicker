import threading
import cv2
import numpy as np
import math
from ultralytics import YOLO
from .storage import save_heatmap_local
from collections import deque
from . import db
from .models import Game, Heatmaps
import time
import threading
import datetime
# Single global worker
stream_worker = None

class StreamWorker(threading.Thread):
    def __init__(self, app, rtmp_url="rtmp://localhost:1935/live/stream", batch_size=1):
        super().__init__(daemon=True)
        self.app = app
        self.rtmp_url = rtmp_url
        self.batch_size =batch_size
        self.game_id = None
        self.cap = cv2.VideoCapture(f"app\\videos\\test.mp4")#self.rtmp_url,cv2.CAP_FFMPEG)
        self.model = YOLO(f"app\\weights\\best.pt")
        self._stop_evt = threading.Event()
        self._processing = threading.Event()
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.move_threshold = 4
        self.previous_loc = [None, None]
        self.frame_buffer = deque(maxlen=batch_size) 
        self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.heatmap_mask = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.latest_frame = None
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.imgsz = 512 
        self.warm_up = False
        self.goal_area_left = (0, self.frame_height//3, 50, self.frame_height*2//3)   # left side box
        self.goal_area_right = (self.frame_width-50, self.frame_height//3, self.frame_width, self.frame_height*2//3)


    def start_processing(self, game_id):
        # Reset heatmap for new session
        print("Started capturing")
        self.game_id = game_id
        self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.previous_loc = [None, None]
        self._processing.set()

    def stop_processing(self):
        print("Stopped capturing")
        if not self._processing.is_set():
            return
        self._processing.clear()
        # Save current heatmap to DB/storage
        if self.heatmap is not None:
            heatmap_norm = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_uint8 = heatmap_norm.astype(np.uint8)
            heatmap_blurred = cv2.GaussianBlur(heatmap_uint8, (25, 25), 0)
            colored_heatmap = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)

            with self.app.app_context():
                _, buffer = cv2.imencode(".png", colored_heatmap)
                image_bytes = buffer.tobytes()
                heatmap_url = save_heatmap_local(game_id=int(time.time()), image_bytes=image_bytes)
                heatmap_entry = Heatmaps.query.filter_by(gameId=self.game_id).first()
                if not heatmap_entry:
                    heatmap_entry = Heatmaps(gameId=self.game_id)
                    db.session.add(heatmap_entry)
                heatmap_entry.Heatmap_Url = heatmap_url

                # Update Game EndDateTime
                game = Game.query.get(self.game_id)
                if game:
                    game.EndDateTime = datetime.datetime.utcnow()

                db.session.commit()
        # Reset heatmap so next start gets a new one
        self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.previous_loc = [None, None]

    def stop(self):
        self._stop_evt.set()
        if self.cap:
            self.cap.release()
    def _camera_loop(self):
        while not self._stop_evt.is_set():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            self.frame_buffer.append(frame.copy())


    def run(self):
        dummy = np.zeros((384, 512, 3), dtype=np.uint8)
        print("Warming up model...")
        for _ in range(3):  # run multiple passes to fully initialize backend
            self.model.predict([dummy], imgsz=self.imgsz, conf=0.5, verbose=False)
        self.warm_up = True
        print("Warmup complete.")

        self.camera_thread.start()
        while not self._stop_evt.is_set():
 

            # Skip processing if not started
            if not self._processing.is_set():
                continue
            if self.heatmap is None:
                self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
            batch_frames = []
            while len(batch_frames) < self.batch_size and len(self.frame_buffer) > 0:
                batch_frames.append(self.frame_buffer.popleft())
            if not batch_frames:
                time.sleep(0.01)
                continue

            # Initialize heatmap if first frame
            if self.heatmap is None:
                self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)

            # YOLO prediction

            print("starting predict", time.time())

            try:
                results = self.model.predict(batch_frames, imgsz=self.imgsz, conf=0.5)
            except Exception as e:
                print("YOLO predict failed:", e)
                continue
            print("should be done processing")
            print("finished predict", time.time())
            for idx, result in enumerate(results):
                print("annotating")
                frame = batch_frames[idx]

                if result.boxes is None or len(result.boxes) == 0:
                    continue

                boxes = result.boxes.xyxy.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy().astype(int)
                confidences = result.boxes.conf.cpu().numpy()

                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.astype(int)
                    cls = classes[i]
                    conf = confidences[i]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"cls {cls} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


                    if cls == 1:
                        if self.previous_loc[1] is not None:
                            dx = cx - self.previous_loc[0]
                            dy = cy - self.previous_loc[1]
                            distance = math.sqrt(dx ** 2 + dy ** 2)
                            if distance < self.move_threshold:
                                continue
                        self.previous_loc = [cx, cy]
                        self.heatmap_mask[:] = 0
                        cv2.circle(self.heatmap_mask, (cx, cy), 25, color=1, thickness=-1)
                        cv2.circle(self.heatmap_mask, (cx, cy), 15, color=2, thickness=-1)
                        cv2.circle(self.heatmap_mask, (cx, cy), 5, color=3, thickness=-1)
                        self.heatmap += self.heatmap_mask


                        
            heatmap_norm = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_uint8 = heatmap_norm.astype(np.uint8)
            heatmap_blurred = cv2.GaussianBlur(heatmap_uint8, (25, 25), 0)
            colored_heatmap = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)

            # Blend heatmap with frame for display
            overlay = cv2.addWeighted(frame, 0.7, colored_heatmap, 0.3, 0)

            self.latest_frame = frame
