# Local & AWS Deployment Guide for TTS App

## A. Local Testing

### 1. Backend (FastAPI)
# Activate virtual environment:

cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies:

pip install -r requirements.txt

# Create .env.local or .env:

AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=<your-region>
AWS_S3_BUCKET=<your-bucket>
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Run FastAPI:

uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test endpoints:

# Voices:

curl http://127.0.0.1:8000/voices

# Generate audio:

curl -X POST http://127.0.0.1:8000/generate-audio \
-H "Content-Type: application/json" \
-d '{"text":"Hello World","voice":"Joanna"}'

### 2. Frontend (Next.js)

# Install dependencies:

cd frontend
npm install

# Create .env.local:

NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
Run app:
npm run dev
Open http://localhost:3000 and test.

### B. AWS Deployment
# 1. Backend Docker & ECR

docker build -t tts-backend .
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag tts-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/tts-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/tts-backend:latest

# 2. ECS Fargate Deployment
Create ECS Cluster (Fargate)
Create Task Definition with:
Container image: ECR URL
Port: 8000
Environment variables from .env
Run service
Access backend:
http://<ecs-public-ip>:8000/docs

## 3. Frontend Deployment

Deploy via Vercel or S3 + CloudFront

.env points to ECS backend:
NEXT_PUBLIC_API_URL=http://<ecs-public-ip>:8000

### C. Testing Flow
/voices returns available Polly voices
Frontend populates <select> automatically
POST /generate-audio with text & voice
Backend uploads MP3 to S3 & returns presigned URL
Frontend <audio> element plays the audio