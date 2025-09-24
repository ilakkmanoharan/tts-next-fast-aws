

### 🟢 If you already created the container before

Run:

```bash
docker ps -a
```

This shows **all containers**, including stopped ones.

* If you see `tts-backend` in the list:
  Start it again:

  ```bash
  docker start -a tts-backend
  ```

  (use `-a` if you want to see logs; otherwise just `docker start tts-backend`)

---

### 🔵 If no container exists yet

Then you must rebuild and run it:

```bash
docker build -t tts-backend:latest .
```

Then start the container:

```bash
docker run -d --name tts-backend -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e BUCKET=your_bucket \
  tts-backend:latest
```

---

After this, check:

```bash
docker ps
```

and you should see something like:

```
CONTAINER ID   IMAGE               STATUS         PORTS                    NAMES
abcd1234       tts-backend:latest  Up 5 seconds   0.0.0.0:8000->8000/tcp   tts-backend
```

Then test:

```bash
curl http://localhost:8000/health
```

---

⚡ Do you want me to write you a **small shell script** that checks if your container exists and either starts it or rebuilds it automatically? That way you won’t have to remember all these steps.


Perfect 👍 That `curl` command just called your `/speak` endpoint successfully!

Here’s what happened step by step:

1. **You sent JSON input** → `{"text": "Hello world"}` to your FastAPI backend.
2. **FastAPI + Polly generated speech** and returned an MP3 file.
3. `curl` wrote that response to `output.mp3`.

Now you can check it:

```bash
ls -lh output.mp3
```

If the file exists, play it with:

```bash
open output.mp3   # on Mac
```

That should play the **“Hello world”** audio 🎶.

---

✅ Your deployment is working locally.
👉 Next step is deciding how you want to **share this app**:

* **Quick & temporary (ngrok)** → instantly get a public HTTPS link.
* **Production (AWS EC2 / Elastic Beanstalk / Fargate)** → more stable, real-world hosting.

Do you want me to guide you through the **ngrok quick-share setup** first?
