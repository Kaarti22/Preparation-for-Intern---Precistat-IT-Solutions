from ultralytics import YOLO
import cv2
import os

model = YOLO("yolov8n.pt")

def detect_objects(input_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.endswith(".jpg"):
            image_path = os.path.join(input_dir, file)
            results = model(image_path)
            annotated_frame = results[0].plot()
            cv2.imwrite(os.path.join(output_dir, file), annotated_frame)