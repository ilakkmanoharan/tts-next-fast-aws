# TTS Web App - Setup Instructions

## 1. Clone Repository
```bash
git clone <repo-url>
cd tts-next-fast-aws
2. Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn boto3 python-dotenv
Environment Variables
Create .env file:
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
Run Backend Locally
uvicorn main:app --reload
Test endpoints:
curl -X POST http://127.0.0.1:8000/generate-audio \
-H "Content-Type: application/json" \
-d '{"text":"Hello World","voice":"Joanna"}'

curl http://127.0.0.1:8000/voices
3. Frontend Setup
cd frontend
npm install
Environment Variables
Create .env.local:
NEXT_PUBLIC_API_URL=http://<your-ecs-public-ip>:8000
Run Frontend
npm run dev
Access app at: http://localhost:3000
4. Deployment on AWS ECS
Create ECS cluster with Fargate
Upload backend Docker container
Configure task with container port 8000 → host port 8000
Assign public IP and security group allowing TCP 8000
Optional: connect CloudFront or Route53 for friendly URL
5. Generate Documentation PDF
brew install pandoc
pandoc docs/setup.md -o docs/setup.pdf
