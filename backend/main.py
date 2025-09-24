import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import os
import uuid

# ------------------- Logger Setup -------------------
logger = logging.getLogger("tts-backend")
logger.setLevel(logging.ERROR)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Rotating file handler (5 MB max, 5 backups)
log_file_path = "/var/log/tts-backend/error.log"  # ECS: ensure writable path
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5*1024*1024, backupCount=5
)
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
    "https://staging-frontend.example.com",
    "https://frontend.example.com",
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
#BUCKET = os.getenv("AWS_S3_BUCKET", "my-bucket")

polly = boto3.client("polly", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

#BUCKET = "ts-audio-ilakkm-aug31"
BUCKET = os.environ.get("BUCKET", "ts-audio-ilakkm-aug31")

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_DEFAULT_REGION")
    )

PREFIX = "_next/"  # Change to any prefix your backend uses

# ------------------- Models -------------------
class TTSRequest(BaseModel):
    text: str
    voice: str = "Joanna"
    engine: str = "neural"

# ------------------- Health Check -------------------
# Assume s3, polly, BUCKET are already initialized
@app.get("/health")
def health_check():
    status = {"status": "ok", "dependencies": {}}
    s3_client = get_s3_client()

    try:
        s3_client.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
        status["dependencies"]["s3"] = "ok"
    except Exception as e:
        status["dependencies"]["s3"] = f"fail ({str(e)})"

    # Polly check
    polly_client = boto3.client("polly")  # can remain same if env vars are fine
    try:
        polly_client.describe_voices()
        status["dependencies"]["polly"] = "ok"
    except Exception as e:
        status["dependencies"]["polly"] = f"fail ({str(e)})"

    if any(v.startswith("fail") for v in status["dependencies"].values()):
        status["status"] = "fail"

    return status


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
        with open(audio_file, "wb") as f:
            f.write(response["AudioStream"].read())
        s3.upload_file(audio_file, BUCKET, audio_file)
        os.remove(audio_file)
    except Exception as e:
        logger.error("Error uploading audio to S3", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

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


#FastAPI Logging for ECS with Rotating Logs
#For ECS / production environments, 
# it’s best to use rotating file logs so your logs don’t fill up the disk. 
# Python’s logging.handlers.RotatingFileHandler can handle this automatically. 


#✅ Production improvements
#Rotating file logs:
#5 MB max per file, 5 backups. Prevents filling up disk in ECS.
#Path: /var/log/tts-backend/error.log (make sure your ECS container has write permissions).
#Console logs are still preserved for CloudWatch or ECS logs aggregation.
#All critical exceptions now log full tracebacks.