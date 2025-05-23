import cv2
import os
import json
from ultralytics import YOLO
from app.logger import logger

model = YOLO("yolo11n.pt")

def detect_persons(video_path, frames_dir, result_path=None):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    person_detected = False
    frame_data = []

    os.makedirs(frames_dir, exist_ok=True)

    logger.info(f"Started processing video: {video_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        results = model(frame)[0]

        frame_filename = os.path.join(frames_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        for box in results.boxes:
            cls = int(box.cls[0])
            if model.names[cls] == "person":
                person_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                frame_data.append({
                    "frame": frame_count,
                    "bbox": [x1, y1, x2, y2],
                    "center": [center_x, center_y]
                })
    
    cap.release()

    result =  {
        "fps": fps,
        "total_frames": frame_count,
        "person_detected": person_detected,
        "frames_with_person": frame_data
    }
    
    if result_path:
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, "w") as f:
            json.dump(result, f, indent=4)
        logger.info(f"Saved result to: {result_path}")
    
    logger.info(f"Finished processing video: {video_path}, frames: {frame_count}, person detected: {person_detected}")
    return result

def is_person_idle(frame_data, fps, idle_seconds=30, movement_threshold=20):
    if not frame_data:
        return False, 0
    
    idle_frame_count = int(idle_seconds * fps)
    idle_start = None

    for i in range(len(frame_data) - idle_frame_count):
        idle = True
        base_center = frame_data[i]["center"]

        for j in range(i + 1, i + idle_frame_count):
            cx, cy = frame_data[j]["center"]
            dx = abs(cx - base_center[0])
            dy = abs(cy - base_center[1])
            if dx > movement_threshold or dy > movement_threshold:
                idle = False
                break
        
        if idle:
            idle_start = frame_data[i]["frame"]
            break
    
    if idle_start:
        idle_duration = (frame_data[-1]["frame"] - idle_start) / fps
        return True, round(idle_duration, 2)
    
    return False, 0