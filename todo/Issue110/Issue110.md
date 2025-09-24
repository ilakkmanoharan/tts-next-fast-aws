Absolutely! Since your Dockerfile is ready, here’s a **step-by-step set of commands to build, run, and test your FastAPI backend locally** before deploying to ECS.

---

### **1️⃣ Build the Docker image**

Run this in your `backend/` directory where the Dockerfile is:

```bash
docker build -t tts-backend:latest .
```

* `-t tts-backend:latest` gives the image a name and tag.

---

### **2️⃣ Run the container locally**

```bash
docker run -it --rm -p 8000:8000 tts-backend:latest
```

* `-p 8000:8000` maps container port 8000 to your local machine.
* `--rm` removes the container after stopping.
* `-it` allows interactive output (you’ll see logs in the terminal).

---

### **3️⃣ Test FastAPI endpoints**

#### **Health check**

```bash
curl http://localhost:8000/health
```

Expected output:

```json
{
  "status": "ok",
  "dependencies": {
    "s3": "ok",
    "polly": "ok"
  }
}
```

If S3 or Polly fails, you’ll see `fail` in the output and logs in `/var/log/tts-backend/error.log`.

---

#### **Root endpoint**

```bash
curl http://localhost:8000/
```

Expected output:

```json
{"message": "Backend is running!"}
```

---

#### **List voices**

```bash
curl http://localhost:8000/voices
```

* Should return a JSON array of Polly voices.

---

#### **Generate audio (test TTS)**

```bash
curl -X POST http://localhost:8000/generate-audio \
-H "Content-Type: application/json" \
-d '{"text":"Hello world","voice":"Joanna","engine":"neural"}'
```

* Should return a JSON response with a pre-signed S3 URL.

---

### **4️⃣ Check logs**

Since your RotatingFileHandler writes to `/var/log/tts-backend/error.log` inside the container:

1. Open a new terminal while the container is running:

```bash
docker exec -it <container_id> /bin/bash
```

* Find the container ID:

```bash
docker ps
```

2. Check logs:

```bash
cat /var/log/tts-backend/error.log
```

* Errors and exceptions will be logged here with timestamps.

---

### **5️⃣ Optional: Remove old containers/images**

```bash
docker ps -a         # List all containers
docker rm <container_id>   # Remove a container
docker images       # List images
docker rmi tts-backend:latest   # Remove image
```

---

If you want, I can give you a **single one-line command to test everything (build, run, and curl health) automatically** so you can verify your backend immediately.

Do you want me to do that?

_______________

Perfect! Here’s a **single one-liner command** that will:

1. Build your Docker image
2. Run it in the background
3. Wait a few seconds for the server to start
4. Curl the `/health` endpoint to verify it’s running

```bash
docker build -t tts-backend:latest . && \
docker run -d --name tts-backend -p 8000:8000 tts-backend:latest && \
echo "Waiting 5 seconds for FastAPI to start..." && sleep 5 && \
curl http://localhost:8000/health
```

---

### **Explanation**

* `docker build -t tts-backend:latest .` → builds the Docker image
* `docker run -d --name tts-backend -p 8000:8000 tts-backend:latest` → runs container in background (`-d`)
* `sleep 5` → gives FastAPI a few seconds to start
* `curl http://localhost:8000/health` → checks that the backend and AWS dependencies (S3, Polly) are healthy

---

### **Optional: Stop and remove the container afterward**

```bash
docker stop tts-backend && docker rm tts-backend
```

---

If you want, I can also give you a **single command that also checks `/voices` and `/generate-audio` endpoints** automatically so you can verify everything in one go.

Do you want me to do that?

_________________________________


Perfect! Here’s a **single command sequence** that will:

1. Build your Docker image
2. Run it in the background
3. Wait for FastAPI to start
4. Test `/health`, `/voices`, and `/generate-audio` endpoints

```bash
docker build -t tts-backend:latest . && \
docker run -d --name tts-backend -p 8000:8000 tts-backend:latest && \
echo "Waiting 5 seconds for FastAPI to start..." && sleep 5 && \
echo "=== Health Check ===" && \
curl http://localhost:8000/health && echo "\n" && \
echo "=== Voices List ===" && \
curl http://localhost:8000/voices && echo "\n" && \
echo "=== Generate Audio ===" && \
curl -X POST http://localhost:8000/generate-audio \
-H "Content-Type: application/json" \
-d '{"text":"Hello world","voice":"Joanna","engine":"neural"}' && echo "\n"
```

---

### **What this does**

* **Health Check** → verifies S3 and Polly connectivity
* **Voices List** → returns available Polly voices
* **Generate Audio** → tests TTS functionality, returning a pre-signed S3 URL

---

### **Optional cleanup after testing**

```bash
docker stop tts-backend && docker rm tts-backend
```

* Stops and removes the container
* Leaves your image intact for future runs

---

If you want, I can also give a **version that captures the logs from `/var/log/tts-backend/error.log` automatically** while testing, so you can see all backend errors in one go.

Do you want me to do that?


____________________________________________

Perfect! Here’s a **one-liner command sequence** that will:

1. Build and run your container
2. Wait for FastAPI to start
3. Test `/health`, `/voices`, and `/generate-audio`
4. Show the contents of `/var/log/tts-backend/error.log` so you can see any logged errors

```bash
docker build -t tts-backend:latest . && \
docker run -d --name tts-backend -p 8000:8000 tts-backend:latest && \
echo "Waiting 5 seconds for FastAPI to start..." && sleep 5 && \
echo "=== Health Check ===" && \
curl http://localhost:8000/health && echo "\n" && \
echo "=== Voices List ===" && \
curl http://localhost:8000/voices && echo "\n" && \
echo "=== Generate Audio ===" && \
curl -X POST http://localhost:8000/generate-audio \
-H "Content-Type: application/json" \
-d '{"text":"Hello world","voice":"Joanna","engine":"neural"}' && echo "\n" && \
echo "=== Error Logs ===" && \
docker exec tts-backend cat /var/log/tts-backend/error.log
```

---

### **Explanation**

* `docker exec tts-backend cat /var/log/tts-backend/error.log` → shows any exceptions that your app logged via the `RotatingFileHandler`.
* You’ll see errors if S3 or Polly connectivity fails, or if any request caused an exception.

---

### **Optional cleanup afterward**

```bash
docker stop tts-backend && docker rm tts-backend
```

---

If you want, I can also give a **version that continuously streams the log** while testing endpoints, so you can watch errors appear live as you hit the API.

Do you want me to do that?
