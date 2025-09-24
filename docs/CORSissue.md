
###### Error

[Error] Origin http://localhost:3000 is not allowed by Access-Control-Allow-Origin. Status code: 500 [Error] Fetch API cannot load http://127.0.0.1:8000/generate-audio due to access control checks. [Error] Failed to load resource: Origin http://localhost:3000 is not allowed by Access-Control-Allow-Origin. Status code: 500 (generate-audio, line 0) [Error] TypeError: Load failed (anonymous function) (app-index.js:33) (anonymous function) (hydration-error-info.js:63) (anonymous function) (page.tsx:68)

This error is a CORS (Cross-Origin Resource Sharing) issue between your React frontend (http://localhost:3000) and your FastAPI backend (http://127.0.0.1:8000).
Your backend is rejecting the request because it hasn’t been configured to allow requests from the frontend’s origin. That’s why you see:
Origin http://localhost:3000 is not allowed by Access-Control-Allow-Origin

Make sure you’re starting the backend with the right host:

uvicorn main:app --reload --host 0.0.0.0 --port 8000


Check that the frontend is calling exactly http://127.0.0.1:8000/generate-audio (not mixing localhost vs 127.0.0.1). CORS treats them as different origins.

