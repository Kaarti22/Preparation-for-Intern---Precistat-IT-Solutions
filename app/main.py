from fastapi import FastAPI, UploadFile, File, HTTPException
from app.logger import logger
from app.processor import extract_frames_opencv, extract_frames_and_audio
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Smart Video Analyzer API is running"}

@app.post("/extract-frames-from-video/")
async def extract_frames_from_video(file: UploadFile = File(...)):
    file_location = f"media/uploads/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    logger.info(f"Uploaded video saved at {file_location}")

    frame_dir = f"media/frames/{file.filename.split('.')[0]}"
    try:
        extract_frames_opencv(file_location, frame_dir, frame_rate=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": f"Frames are extracted from {file.filename}",
        "frames_dir": frame_dir
    }

@app.post("/extract-frames-and-audio/")
async def extract_frames_and_audio_from_video(file: UploadFile = File(...)):
    file_location = f"media/uploads/{file.filename}"
    os.makedirs("media/uploads", exist_ok=True)
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    
    logger.info(f"Uploaded video saved at {file_location}")

    output_dir = f"media/frames/{file.filename.rsplit('.', 1)[0]}"
    try:
        result = extract_frames_and_audio(file_location, output_dir, frame_rate=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": f"Frames and audio extracted from {file.filename}",
        "frames_dir": result["frames_dir"],
        "audio_file": result["audio_file"] or "No audio stream found"
    }