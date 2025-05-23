from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.logger import logger
from app.video_processor import detect_persons, is_person_idle

app = FastAPI()

MEDIA_UPLOADS = "media/uploads"
MEDIA_FRAMES = "media/frames"
MEDIA_RESULTS = "media/results"

@app.get("/")
def read_root():
    return {"message": "Smart Video Analyzer API is running"}

@app.post("/analyze/")
async def analyze_video(file: UploadFile = File(...)):
    os.makedirs(MEDIA_UPLOADS, exist_ok=True)

    upload_path = os.path.join(MEDIA_UPLOADS, file.filename)
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Uploaded video saved at: {upload_path}")
    
    filename_base = os.path.splitext(file.filename)[0]
    frames_dir = os.path.join(MEDIA_FRAMES, filename_base)
    result_path = os.path.join(MEDIA_RESULTS, f"{filename_base}.json")

    data = detect_persons(upload_path, frames_dir, result_path)
    idle_detected, idle_duration =is_person_idle(data["frames_with_person"], data["fps"])

    logger.info(f"Idle detected: {idle_detected}, duration: {idle_duration}")

    return {
        "person_detected": data["person_detected"],
        "idle_detected": idle_detected,
        "idle_duration": f"{idle_duration} seconds" if idle_detected else "0 seconds",
        "frames_tracked": len(data["frames_with_person"]),
        "total_frames": data["total_frames"],
        "result_path": result_path
    }