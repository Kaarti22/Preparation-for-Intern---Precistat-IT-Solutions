import ffmpeg
import os
import cv2
from ultralytics import YOLO
from app.logger import logger

def extract_frames_opencv(video_path: str, output_frame_dir: str, frame_rate: int = 1):
    os.makedirs(output_frame_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.info(f"Error: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps // frame_rate)

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_frame_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    logger.info(f"Extracted {saved_count} frames at {frame_rate} fps to '{output_frame_dir}'.")

def extract_frames_and_audio(video_path: str, output_dir: str, frame_rate: int = 1):
    os.makedirs(output_dir, exist_ok=True)

    frames_path = os.path.join(output_dir, "frame_%04d.jpg")
    ffmpeg.input(video_path).output(frames_path, r=frame_rate).run(overwrite_output=True)
    logger.info(f"Extracted frames to {output_dir}")

    try:
        probe = ffmpeg.probe(video_path)
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        if audio_streams:
            audio_path = os.path.join(output_dir, "audio.wav")
            ffmpeg.input(video_path).output(audio_path, acodec='pcm_s16le', ac=2, ar='44100').run(overwrite_output=True)
            logger.info(f"Extracted audio to {audio_path}")
            return {
                "frames_dir": output_dir,
                "audio_file": audio_path
            }
        else:
            logger.info(f"No audio stream found in {video_path}.")
            return {
                "frames_dir": output_dir,
                "audio_file": None
            }
    except ffmpeg.Error as e:
        logger.info("FFmpeg error while checking audio stream: ", e)

def run_yolo_detection_on_frames(frame_dir: str, model_path: str = "yolo11n.pt"):
    model = YOLO(model_path)

    detected_frames_dir = os.path.join(frame_dir, "detected")
    os.makedirs(detected_frames_dir, exist_ok=True)

    results_summary = []

    for filename in sorted(os.listdir(frame_dir)):
        if filename.endswith(".jpg"):
            frame_path = os.path.join(frame_dir, filename)
            result = model(frame_path)

            result[0].save(filename=os.path.join(detected_frames_dir, filename))

            boxes = result[0].boxes
            objects = [model.names[int(cls)] for cls in boxes.cls] if boxes else []
            results_summary.append({
                "frame": filename,
                "objects_detected": objects
            })
        
    logger.info("YOLO detection has completed successfully.")
    return detected_frames_dir, results_summary