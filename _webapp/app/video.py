from flask import Flask, Response, current_app, app, stream_with_context
import cv2
from flask import Blueprint, render_template, redirect, url_for, request, flash

video_bp = Blueprint("video", __name__)

def generate_frames():
    while True:
        frame = current_app.stream_worker.latest_frame
        if frame is None:
            continue  # skip until a frame is ready

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        # Yield frame in MJPEG format
        #yield frame_bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
@video_bp.route('/video_feed')
def video_feed():
    with current_app.app_context():
        #return Response(stream_with_context(generate_frames()), mimetype='image/jpeg')
        
        return Response(stream_with_context(generate_frames()),
                         mimetype='multipart/x-mixed-replace; boundary=frame')