# TTS Web App - Specifications

## Overview
A web-based Text-to-Speech (TTS) application using React, Next.js (frontend) and FastAPI (backend) deployed on AWS. Users can type/paste text and convert it into speech, choosing from multiple Polly voices. The generated audio is stored in S3 and streamed back to the user.

---

## Tech Stack

### Frontend
- **Framework:** React 18 / Next.js App Router
- **Languages:** TypeScript, CSS
- **Key Components:**
  - `page.tsx` – main page with text input, voice selector, and submit button.
  - `VoiceSelector.tsx` – dynamic voice dropdown fetching voices from FastAPI `/voices`.

### Backend
- **Framework:** FastAPI
- **Languages:** Python 3.13
- **Libraries:** boto3, python-dotenv, pydantic
- **Endpoints:**
  - `POST /generate-audio` – Converts text to audio using AWS Polly, stores in S3, returns presigned URL.
  - `GET /voices` – Returns list of available AWS Polly voices.

### AWS Services
- **Polly:** Text-to-speech synthesis
- **S3:** Stores generated audio files, presigned URLs for access
- **ECS (Fargate):** Hosts FastAPI backend
- **CloudFront / Route53 (Optional):** For custom domain and HTTPS distribution
- **Environment Variables:** Stored in `.env.local` and `.env` for local dev
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`
  - `AWS_S3_BUCKET`
  - `NEXT_PUBLIC_API_URL`

### Deployment
- **ECS Fargate:** 20 GiB ephemeral storage, public IP: `34.237.144.83`
- **Frontend:** Next.js app deployed on Vercel or same ECS cluster
- **Networking:** ECS task binds container port 8000 to host port 8000 (TCP)

---

## Features
- Dynamic voice selection from AWS Polly
- Handles text input up to 5000 words (long text splitting required)
- Plays audio directly in browser
- Shows loading state and error messages
- Presigned URLs valid for 1 hour
