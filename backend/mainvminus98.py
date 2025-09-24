from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import os
import uuid
import logging

# ------------------- Logging Setup -------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Capture ERROR and CRITICAL messages

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# File handler
file_handler = logging.FileHandler("error.log", mode="a")
file_handler.setLevel(logging.ERROR)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ------------------- FastAPI app -------------------
app = FastAPI()

# ------------------- Enable CORS -------------------
origins = [
    "http://ilakkmanoharan5840-frontend.s3-website-us-east-1.amazonaws.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://staging-frontend.example.com",  # staging frontend
    "https://frontend.example.com",          # production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- AWS Clients -------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET = os.getenv("AWS_S3_BUCKET", "my-bucket")

polly = boto3.client("polly", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

# ------------------- Models -------------------
class TTSRequest(BaseModel):
    text: str
    voice: str = "Joanna"
    engine: str = "neural"

# ------------------- Health Check Endpoint -------------------
@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.get("/health")
async def health_check():
    status = {"s3": "ok", "polly": "ok"}
    http_status = 200

    # Check S3
    try:
        s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
    except s3.exceptions.ClientError as e:
        logger.error("S3 health check failed", exc_info=True)
        error_code = e.response["Error"]["Code"]
        status["s3"] = f"fail ({error_code}) - check IAM task role and bucket name"
        http_status = 500

    # Check Polly
    try:
        polly.describe_voices(MaxResults=1)
    except Exception as e:
        logger.error("Polly health check failed", exc_info=True)
        status["polly"] = f"fail ({str(e)})"
        http_status = 500

    if http_status == 200:
        return JSONResponse({"status": "ok", "dependencies": status})
    else:
        return JSONResponse({"status": "fail", "dependencies": status}, status_code=http_status)

# ------------------- Voices Endpoint -------------------
@app.get("/voices")
async def list_voices():
    try:
        voices_list = []
        paginator = polly.get_paginator("describe_voices")

        for page in paginator.paginate():
            for v in page["Voices"]:
                voices_list.append({
                    "id": v["Id"],
                    "name": v.get("Name"),
                    "languageCode": v.get("LanguageCode"),
                    "languageName": v.get("LanguageName"),
                    "gender": v.get("Gender"),
                    "engines": v.get("SupportedEngines", [])
                })

        return JSONResponse({"voices": voices_list})

    except Exception as e:
        logger.error("Error listing Polly voices", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

# ------------------- TTS Endpoint -------------------
@app.post("/generate-audio")
async def generate_audio(request: TTSRequest):
    try:
        response = polly.synthesize_speech(
            Text=request.text,
            OutputFormat="mp3",
            VoiceId=request.voice,
            Engine=request.engine
        )
    except polly.exceptions.InvalidParameterValueException:
        logger.error("Invalid TTS request", exc_info=True)
        return JSONResponse(
            {"error": "Invalid voice or text too long / engine not supported"},
            status_code=400
        )
    except Exception as e:
        logger.error("Error generating audio", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

    audio_file = f"{uuid.uuid4()}.mp3"

    try:
        # Save locally and upload to S3
        with open(audio_file, "wb") as f:
            f.write(response["AudioStream"].read())
        s3.upload_file(audio_file, BUCKET, audio_file)
        os.remove(audio_file)
    except Exception as e:
        logger.error("Error uploading audio to S3", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

    # Generate presigned URL
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": audio_file},
            ExpiresIn=3600
        )
    except Exception as e:
        logger.error("Error generating presigned URL", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"url": url, "engine": request.engine, "voice": request.voice})


#✅ What changed
#Added file handler (error.log) along with console handler.
#All logger.error(..., exc_info=True) calls remain, so full tracebacks are logged to both console and file.
#File logs append (mode="a") to preserve past errors.
