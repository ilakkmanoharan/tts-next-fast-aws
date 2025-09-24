ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % docker build -t tts-backend:latest . && \
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

[+] Building 0.1s (1/1) FINISHED                                                                                                                   docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                               0.0s
 => => transferring dockerfile: 2B                                                                                                                                 0.0s
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory

The error is clear: Docker cannot find your `Dockerfile` in the current directory. Right now, you’re running:

```bash
docker build -t tts-backend:latest .
```

The `.` means “look in the current directory for a `Dockerfile`.” Since it says:

```
failed to read dockerfile: open Dockerfile: no such file or directory
```

…it means either:

1. **The `Dockerfile` doesn’t exist in your current directory** (`tts-next-fast-aws`), or
2. **It’s named differently**, like `dockerfile` (lowercase) or `Dockerfile.dev`.

✅ Fixes:

* Make sure you are in the directory where the `Dockerfile` actually is:

```bash
ls -l
```

You should see a file named exactly `Dockerfile`.

* If it exists with a different name, specify it with `-f`:

```bash
docker build -f Dockerfile.dev -t tts-backend:latest .
```

Once the Docker build succeeds, your full chain of commands (`docker run`, `curl`, etc.) should work.

If you want, I can give you a **one-liner that checks for the Dockerfile and runs your health/audio tests automatically** so you don’t hit this again. Do you want me to do that?

