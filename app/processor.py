import ffmpeg
import subprocess
import os
import cv2

def has_audio_stream(input_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return bool(result.stdout.strip())

def extract_audio(input_path, output_path):
    if not has_audio_stream(input_path):
        raise ValueError("No audio stream found in the video.")

    ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le', ac=1, ar='16000').run()

def extract_frames(video_path: str, output_frame_dir: str):
    os.makedirs(output_frame_dir, exist_ok=True)
    ffmpeg.input(video_path).output(f"{output_frame_dir}/frame_%04d.jpg", r=1).run(overwrite_output=True)

def extract_frames_opencv(video_path: str, output_frame_dir: str, frame_rate: int = 1):
    os.makedirs(output_frame_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
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
    print(f"Extracted {saved_count} frames at {frame_rate} fps to '{output_frame_dir}'.")    