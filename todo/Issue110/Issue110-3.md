ilakkuvaselvimanoharan@MacBookPro backend % docker ps -a

CONTAINER ID   IMAGE                COMMAND                  CREATED         STATUS                     PORTS                                         NAMES
17fad69a5a49   tts-backend:latest   "uvicorn main:app --…"   2 minutes ago   Up 2 minutes               0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   tts-backend
267f9f952e11   663598aae256         "uvicorn main:app --…"   3 weeks ago     Exited (255) 12 days ago   0.0.0.0:8000->8000/tcp                        clever_banzai


Great — the container is actually **up** (`STATUS: Up 2 minutes`), which means it didn’t immediately crash. The `Recv failure: Connection reset by peer` suggests the FastAPI app **started but then reset the connection** when `/health` was called. This usually happens if:

---

### 1️⃣ FastAPI crashes internally on the first request

Check your logs inside the container:

```bash
docker logs tts-backend
```

Look for Python exceptions, missing imports, or AWS-related errors (S3, Polly, etc.), which often break the request handling.

---

### 2️⃣ `/health` endpoint itself has an error

If your `/health` endpoint references any services (like S3, Polly, database) without proper credentials or network access, it may raise an exception, closing the connection.

---

### 3️⃣ File permissions / missing directories

You created `/var/log/tts-backend`, but if your app tries to write logs to a different path or lacks permission, it can crash when handling requests.

Check inside container:

```bash
docker exec -it tts-backend ls -l /var/log/tts-backend
docker exec -it tts-backend cat /var/log/tts-backend/error.log
```

---

### 🔹 Immediate debugging steps

1. Tail logs in real time:

```bash
docker logs -f tts-backend
```

2. Try running uvicorn **manually inside the container** to see immediate errors:

```bash
docker exec -it tts-backend bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

This will show any Python traceback immediately when you hit `/health`.

---

If you want, I can **write a minimal debug command** that runs your container with full logging to `/var/log/tts-backend/error.log` and keeps stdout, so you can see exactly why `/health` fails.

Do you want me to do that?
