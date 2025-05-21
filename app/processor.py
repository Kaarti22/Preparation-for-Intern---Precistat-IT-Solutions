import ffmpeg
import subprocess
import os

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