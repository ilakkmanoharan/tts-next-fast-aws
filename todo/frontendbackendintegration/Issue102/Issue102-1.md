Oof — a 500 from `/health` is usually the app itself throwing an exception. Below is a focused, **ordered** troubleshooting checklist you can run now (local → container → cloud) with exact commands and code snippets. Work top-to-bottom until the error is resolved.

# Quick summary

A `500` on `/health` means the FastAPI process handled the request but an exception occurred in the route (or in a dependency called by it). Usual culprits: missing env vars, failing DB connection, import-time errors, unhandled exceptions in dependency injection, or mis-routed requests (router prefix mismatch).

---

# Step-by-step debugging (do these now)

## 1) Capture the full HTTP response and headers

Run this to see status, headers, and body:

```bash
curl -i -sS -X GET "$BACKEND_URL/health" -H "Accept: application/json" -v
```

(If `BACKEND_URL` is set in your environment, use it; otherwise paste the full URL.)

Look for any body message or trace. If there is no useful body, proceed.

---

## 2) Reproduce locally (quickest way to iterate)

From your project dir:

```bash
# start with verbose logging
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
# then curl the endpoint locally:
curl -i http://127.0.0.1:8000/health
```

If the endpoint works locally, the problem is deployment-specific (env, packaging, or infra).

---

## 3) Check the app logs / stack trace (wherever the app runs)

* **Local / dev**: `uvicorn` prints stack traces to stdout.
* **Docker container**:

  ```bash
  docker ps
  docker logs -f <container_id_or_name>
  ```
* **Kubernetes**:

  ```bash
  kubectl get pods -n <ns>
  kubectl logs -f <pod-name> -c <container-name>
  kubectl describe pod <pod-name> -n <ns>   # check events
  ```
* **ECS / Fargate or Lambda**: check CloudWatch logs (console or AWS CLI). Example CLI:

  ```bash
  # tail logs (AWS CLI v2)
  aws logs tail "/ecs/your-service-log-group" --since 1h --follow
  # or for Lambda:
  aws logs describe-log-streams --log-group-name "/aws/lambda/your-function" --order-by LastEventTime --descending
  aws logs get-log-events --log-group-name "/aws/lambda/your-function" --log-stream-name "<stream-name>" --limit 50
  ```

Read the stack trace — it will point to the failing module / line.

---

## 4) Common error sources & what to check (do these quickly)

* **Import-time / startup exceptions**: If your module raises while importing (top-level code) the route might exist but code will throw on call. Search for code that runs on import.

  * Quick grep: `grep -R "DATABASE_URL\|AWS_SECRET\|SOME_SERVICE" -n .`
* **Missing environment variables**: print them in the running environment.

  * In container: `docker exec -it <container> printenv | grep -E 'DB|DATABASE|AWS|SECRET|URL'`
  * In k8s: `kubectl exec -it <pod> -- printenv | grep -E 'DB|DATABASE|AWS|SECRET|URL'`
* **DB or external API calls inside /health**: If `/health` connects to DB/third party and that fails, the route will 500. Temporarily remove/guard those checks.
* **Wrong route prefix**: You might be hitting `/health` while your app uses a prefix (e.g. `/api/health`). Inspect `app.include_router(..., prefix=...)`.
* **Unhandled exceptions in dependency injection** (e.g. Depends(...) that raises) — wrap dependency code with try/except and log.

---

## 5) Minimal safe `/health` to use while debugging

Replace your current `/health` with this temporary lightweight handler that avoids heavy checks:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

If this returns 200, the problem is whatever checks the original endpoint performed (DB, S3, etc.). Use this as a fallback so your load balancer / ALB / ALB health check can pass while you debug deeper.

---

## 6) If your health route *should* check DB / other services — add safe error handling

Example (SQLAlchemy async check):

```python
from fastapi import HTTPException

@app.get("/ready")
async def ready():
    try:
        # replace with whatever quick lightweight check you have
        await db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        # Do NOT expose e in production; log it instead
        logger.exception("readiness check failed")
        raise HTTPException(status_code=503, detail="not ready")
```

Use `/health` for liveness (process alive) and `/ready` for readiness (depends on DB).

---

## 7) Verify environment variable handling (Pydantic BaseSettings example)

If you rely on `.env`, ensure your settings class points to it and that the file is present in the runtime environment:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AWS_REGION: str = "us-east-1"
    class Config:
        env_file = ".env"

settings = Settings()  # will raise ValidationError if required vars missing
```

**Important:** In production you should pass env vars via the platform (ECS task definition, Kubernetes secrets, Lambda env vars), not rely on copying `.env` into the image.

---

## 8) If running inside Docker — common packaging pitfalls

* Confirm installed deps: `docker exec -it <container> pip freeze | head`
* Confirm working directory: `docker exec -it <container> ls -la`
* Confirm the process command logs: check the container startup command (in `docker-compose.yml` or Dockerfile `CMD`).
* If you used a multi-stage build, ensure you didn't forget to copy `app` code into final image.

---

## 9) If behind API Gateway / ALB / CloudFront — verify the route mapping

* Hitting the gateway -> check **integration response** and mapping templates. Gateway could translate errors into 500.
* Try to curl the backend directly (bypass API Gateway) if possible to determine if the error is from the backend or the gateway.

---

## 10) Add temporary logging in `/health` to surface errors

Modify your health handler to log the exception and return a small error body (only for debugging):

```python
import logging
from fastapi import HTTPException

logger = logging.getLogger("uvicorn.error")

@app.get("/health")
async def health():
    try:
        # example: check DB or other dependency
        await maybe_check_db()
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Health check failed")
        # return a small non-sensitive message in the response for debugging
        raise HTTPException(status_code=500, detail="health check failed (see server logs)")
```

Then tail the logs and reproduce a request to see the full stacktrace.

---

## 11) If the stack trace points to an import or missing dependency

* Add `pip show <package>` inside the runtime environment or check `requirements.txt` vs what's installed.
* If the stack trace shows `ModuleNotFoundError: X`, rebuild your image adding that package.

---

## 12) If using gunicorn + uvicorn workers — ensure logs aren’t swallowed

Start with:

```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --log-level debug --capture-output
```

`--capture-output` forces stdout/stderr capture so logs appear in container logs.

---

## 13) Quick actionable checklist (run these immediately)

1. `curl -i -v $BACKEND_URL/health`  — view raw response & headers
2. Start locally: `uvicorn main:app --reload --log-level debug` and `curl` locally
3. Tail logs where app runs (`docker logs -f`, `kubectl logs -f`, or CloudWatch tail)
4. Replace `/health` with the **minimal** handler above; retest
5. If minimal handler works, reintroduce checks one-by-one (DB → cache → external API) and repeat
6. Look for missing env vars: `printenv | grep -E 'DB|DATABASE|AWS|SECRET|URL'` in runtime
7. If DB-related, test a one-off DB connection from the runtime (python REPL or small script)
8. Add `logger.exception()` in the handler to see full traceback in logs

---

## 14) Preventative improvements (once fixed)

* Separate **liveness** (`/health`) from **readiness** (`/ready`) endpoints.
* Make readiness checks lightweight and time-limited (timeout external calls).
* Add structured logging and Sentry/Bugsnag to capture exceptions.
* Use built-in platform secrets (K8s secrets, ECS task env, Lambda env vars) rather than copying `.env` to images.


next step: paste **(a)** the current `/health` route implementation and **(b)** the last 30 lines of logs from your running deployment (or the CloudWatch log snippet). I’ll read them and point to the exact failing line and a fixed patch.
