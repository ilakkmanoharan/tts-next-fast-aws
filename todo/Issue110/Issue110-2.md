ilakkuvaselvimanoharan@MacBookPro backend % docker build -t tts-backend:latest . && \
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

[+] Building 0.9s (11/11) FINISHED                                                                                                                 docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                               0.0s
 => => transferring dockerfile: 985B                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.12-slim                                                                                                0.4s
 => [internal] load .dockerignore                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                    0.0s
 => [1/6] FROM docker.io/library/python:3.12-slim@sha256:abc799c7ee22b0d66f46c367643088a35e048bbabd81212d73c2323aed38c64f                                          0.0s
 => => resolve docker.io/library/python:3.12-slim@sha256:abc799c7ee22b0d66f46c367643088a35e048bbabd81212d73c2323aed38c64f                                          0.0s
 => [internal] load build context                                                                                                                                  0.4s
 => => transferring context: 858.18kB                                                                                                                              0.4s
 => CACHED [2/6] WORKDIR /app                                                                                                                                      0.0s
 => CACHED [3/6] COPY requirements.txt .                                                                                                                           0.0s
 => CACHED [4/6] RUN pip install --no-cache-dir -r requirements.txt                                                                                                0.0s
 => CACHED [5/6] COPY . .                                                                                                                                          0.0s
 => CACHED [6/6] RUN mkdir -p /var/log/tts-backend && chmod 777 /var/log/tts-backend                                                                               0.0s
 => exporting to image                                                                                                                                             0.1s
 => => exporting layers                                                                                                                                            0.0s
 => => exporting manifest sha256:55fa4437b9727b8c4541e29b125e7e53d85a3dbc09d6a1c836c4b0c2f6606d24                                                                  0.0s
 => => exporting config sha256:8ee69f517a897cb4c3ea0afd6c3afcda8dc58caf74848c4b6838752444b85512                                                                    0.0s
 => => exporting attestation manifest sha256:c83b383d5ff8916779476602aa9c76116d97139ab0e3daccfd5205851660d71f                                                      0.0s
 => => exporting manifest list sha256:bada037900b9238c12cbe18887abfe44eabdc332d5eaaca48520d7a34670fa04                                                             0.0s
 => => naming to docker.io/library/tts-backend:latest                                                                                                              0.0s
 => => unpacking to docker.io/library/tts-backend:latest                                                                                                           0.0s
17fad69a5a490969665d830ed0052f1350dbb54ce693cde02e0739bf5a7c1829
Waiting 5 seconds for FastAPI to start...
=== Health Check ===
curl: (56) Recv failure: Connection reset by peer


The `curl: (56) Recv failure: Connection reset by peer` error indicates that your FastAPI app inside the container started but immediately crashed or failed to bind to the port. This is why the health check fails. Common causes:

---

### 1️⃣ FastAPI is not running or crashed

Check if the container is still running:

```bash
docker ps -a
```

If it exited, check the logs:

```bash
docker logs tts-backend
```

This will usually show Python exceptions or missing dependencies.

---

### 2️⃣ FastAPI is bound to the wrong interface

Inside Docker, FastAPI must bind to `0.0.0.0` (not `127.0.0.1`). In `main.py` or your startup command, it should be:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 3️⃣ Missing dependencies or runtime errors

Even if `pip install` succeeded, runtime errors (like missing AWS credentials, invalid environment variables, or missing model files) can crash the app immediately.

---

### 4️⃣ Port mapping conflicts

You mapped `-p 8000:8000`, which is fine if nothing else is on port 8000 on your host. Ensure no other process is using port 8000:

```bash
lsof -i :8000
```

---

### ✅ Next steps to debug

1. Check container status:

```bash
docker ps -a
```

2. Inspect logs for Python exceptions:

```bash
docker logs tts-backend
```

3. Verify that `uvicorn` runs with `host="0.0.0.0"` and port `8000`.

---

If you want, I can give you a **ready-to-run command to start the container with proper logging and keep it from crashing**, so you can immediately test `/health` and `/voices`.

Do you want me to do that?
