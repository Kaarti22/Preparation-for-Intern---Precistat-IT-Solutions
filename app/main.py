from fastapi import FastAPI, UploadFile, File, HTTPException
from app.logger import logger
from app.processor import extract_audio, extract_frames
from app.detector import detect_objects

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Smart Video Analyzer API is running"}

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    file_location = f"media/uploads/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    logger.info(f"Uploaded video saved at {file_location}")
    
    audio_path = f"media/audio/{file.filename.split('.')[0]}.wav"
    frame_dir = f"media/frames/{file.filename.split('.')[0]}"
    output_dir = f"media/outputs/{file.filename.split('.')[0]}"

    try:
        extract_audio(file_location, audio_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    extract_frames(file_location, frame_dir)
    detect_objects(frame_dir, output_dir)

    logger.info(f"{file.filename} has been processed")

    return {
        "message": f"{file.filename} processed.",
        "frames_dir": output_dir,
        "audio_path": audio_path
    }