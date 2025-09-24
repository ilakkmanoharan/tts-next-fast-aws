Backend Health check failed (500 errors)
The script hit $BACKEND_URL/health and consistently got HTTP 500.
This means your FastAPI backend is running but throwing an error in the /health route (or something upstream, like Lambda, ECS, or API Gateway, is misconfigured).
Debug steps:
Check backend logs (FastAPI app logs, Lambda logs in CloudWatch, or ECS container logs).
Make sure your /health endpoint is correctly implemented. For example:
@app.get("/health")
async def health():
    return {"status": "ok"}
Verify that your backend actually starts up without missing environment variables (e.g., AWS credentials, DB URL, etc.). A common issue is .env not being picked up in deployment.