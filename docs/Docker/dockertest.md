
Rebuild Docker image:

docker build -t tts-backend:latest .

Push the new image to your repository and update ECS service to use it.

You have several Docker images locally. The key one you just built is:

```
REPOSITORY: tts-backend
TAG: latest
IMAGE ID: e8b085c8ef51
SIZE: 473MB
```

Other images include older builds and some ECR images for your project.

Some things you might want to do next:

---

### 1. **Run your new backend image**

```bash
docker run -it --rm -p 8000:8000 tts-backend:latest
```

* Maps container port `8000` to your host.
* `--rm` removes the container when it stops.
* Adjust the port if your FastAPI app uses a different one.

---

### 2. **Tag and push to ECR (if needed)**

If you want to push `tts-backend:latest` to your AWS ECR:

```bash
docker tag tts-backend:latest 681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend:latest
docker push 681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend:latest
```

---

### 3. **Clean up dangling/unused images**

You have some `<none>` images (dangling). To remove them:

```bash
docker image prune
```

Or remove a specific image:

```bash
docker rmi IMAGE_ID
```

Example:

```bash
docker rmi fcbe623d1302
```

---

Next step::  I can give you a **quick command to clean up all old/unused images while keeping your latest tts-backend**—it’s very handy. 

-----

Great! You can clean up all unused or dangling Docker images **without touching your latest `tts-backend` image** using these steps.

---

### 1. **Remove all dangling images**

Dangling images are `<none>` images that aren’t tagged and take up space:

```bash
docker image prune -f
```

---

### 2. **Remove all unused images except the ones you want to keep**

First, get the IMAGE ID of the images you **want to keep**:

```bash
docker images tts-backend
```

Example output:

```
REPOSITORY      TAG     IMAGE ID
tts-backend     latest  e8b085c8ef51
```

Here, `e8b085c8ef51` is the one to keep. Then remove all other images **except this one**:

```bash
docker images -q | grep -v e8b085c8ef51 | xargs docker rmi -f
```

* `docker images -q` → lists all image IDs.
* `grep -v IMAGE_ID` → excludes the image you want to keep.
* `xargs docker rmi -f` → forcibly removes the rest.

---

### ✅ Result

* Only your latest `tts-backend` remains.
* Disk space is cleared of old and dangling images.

---

Next step::: I can give you an **even safer one-liner** that keeps **all your project-related images** but removes everything else to free space. It’s usually safer on multi-image projects. 
________


Here’s a **safe one-liner** that keeps all your project-related images (`tts-backend` and any ECR images from your project) but removes everything else:

```bash
docker images -q | grep -vE "(tts-backend|tts-next-fast-aws|tts-next-fast-backend)" | xargs -r docker rmi -f
```

### How it works:

* `docker images -q` → lists all image IDs.
* `grep -vE "(tts-backend|tts-next-fast-aws|tts-next-fast-backend)"` → **excludes** all images that match your project names.
* `xargs -r docker rmi -f` → forcibly removes all the other images. (`-r` prevents errors if there’s nothing to remove)

✅ This keeps all your project images intact while cleaning up unrelated images (like old Supabase images or dangling images).

You can also follow this with:

```bash
docker image prune -f
```

…to clear any leftover dangling layers.

Next step:: I can give you a **one-line command that cleans everything except your latest `tts-backend` AND your ECR images automatically**, without manually listing names. 