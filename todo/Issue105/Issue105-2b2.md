 copilot svc show --name backend
About

  Application  tts-next-fast-aws
  Name         backend
  Type         Load Balanced Web Service

Configurations

  Environment  Tasks     CPU (vCPU)  Memory (MiB)  Platform      Port
  -----------  -----     ----------  ------------  --------      ----
  dev          1         0.25        512           LINUX/X86_64  8000

Routes

  Environment  URL
  -----------  ---
  dev          http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com

Internal Service Endpoints

  Endpoint                                  Environment  Type
  --------                                  -----------  ----
  backend.dev.tts-next-fast-aws.local:8000  dev          Service Discovery

Variables

  Name                                Container  Environment  Value
  ----                                ---------  -----------  -----
  COPILOT_APPLICATION_NAME            backend    dev          tts-next-fast-aws
  COPILOT_ENVIRONMENT_NAME              "          "          dev
  COPILOT_LB_DNS                        "          "          tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com
  COPILOT_SERVICE_DISCOVERY_ENDPOINT    "          "          dev.tts-next-fast-aws.local
  COPILOT_SERVICE_NAME                  "          "          backend
  ENV                                   "          "          dev
ilakkuvaselvimanoharan@MacBookPro backend % 

Got it — thanks for pasting.

👉 Notice in the `Variables` section: **`AWS_S3_BUCKET` is missing**.
That means your `copilot svc deploy` earlier with `--resource-tags AWS_S3_BUCKET=...` didn’t actually create an environment variable.

---

### ✅ Why?

* `--resource-tags` adds *tags* to AWS resources, not container environment variables.
* To inject env vars into the container, you need `variables:` in `copilot/backend/manifest.yml`.

---

### 🔧 Fix

Edit `copilot/backend/manifest.yml` and add:

```yaml
variables:
  AWS_S3_BUCKET: ts-audio-ilakkm-aug31
```

Then redeploy:

```bash
copilot svc deploy --name backend --env dev
```

---

### ✅ After redeploy

Run:

```bash
copilot svc show --name backend
```

You should then see:

```
Variables

  Name             Container  Environment  Value
  ----             ---------  -----------  -----
  AWS_S3_BUCKET    backend    dev          ts-audio-ilakkm-aug31
  COPILOT_...
```

---

⚡ That will make your `/health` check hit the **real bucket** instead of defaulting to `"my-bucket"`.

Do you want me to draft the exact section of your current `manifest.yml` with the right indentation so you can just paste it in?

