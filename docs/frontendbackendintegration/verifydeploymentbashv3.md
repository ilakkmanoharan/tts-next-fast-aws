Here’s an **enhanced Bash script** that automatically retries failed checks and reports detailed errors. This is ideal for CI/CD pipelines or post-deploy verification.

```bash
#!/bin/bash

FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
BACKEND_URL="http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com"
MAX_RETRIES=3
SLEEP_INTERVAL=5  # seconds between retries

# Retry function
retry_check() {
    local url=$1
    local description=$2
    local max_retries=$3
    local attempt=1

    while [ $attempt -le $max_retries ]; do
        HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $url)
        if [ "$HTTP_STATUS" -eq 200 ]; then
            echo "✅ $description reachable: $HTTP_STATUS (Attempt $attempt)"
            return 0
        else
            echo "⚠️ $description check failed: $HTTP_STATUS (Attempt $attempt)"
            if [ $attempt -lt $max_retries ]; then
                echo "   Retrying in $SLEEP_INTERVAL seconds..."
                sleep $SLEEP_INTERVAL
            fi
        fi
        attempt=$((attempt + 1))
    done
    echo "❌ $description not reachable after $max_retries attempts"
    return 1
}

# Frontend check
echo "🔎 Checking Frontend..."
retry_check "$FRONTEND_URL" "Frontend" $MAX_RETRIES

# Backend health check
echo -e "\n🔎 Checking Backend Health..."
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    BACKEND_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/backend_response.txt $BACKEND_URL/health)
    HTTP_BODY=$(cat /tmp/backend_response.txt)
    if [ "$BACKEND_RESPONSE" -eq 200 ]; then
        echo "✅ Backend reachable: $BACKEND_RESPONSE, response: $HTTP_BODY (Attempt $attempt)"
        break
    else
        echo "⚠️ Backend check failed: $BACKEND_RESPONSE, response: $HTTP_BODY (Attempt $attempt)"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "   Retrying in $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        else
            echo "❌ Backend not reachable after $MAX_RETRIES attempts"
        fi
    fi
    attempt=$((attempt + 1))
done

# Frontend-backend integration check
echo -e "\n🔎 Checking Frontend-Backend Integration..."
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    INTEGRATION_STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL/api/test)
    INTEGRATION_BODY=$(cat /tmp/integration_response.txt)
    if [ "$INTEGRATION_STATUS" -eq 200 ]; then
        echo "✅ Integration OK: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
        break
    else
        echo "⚠️ Integration check failed: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "   Retrying in $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        else
            echo "❌ Integration not OK after $MAX_RETRIES attempts"
        fi
    fi
    attempt=$((attempt + 1))
done

# Clean up temp files
rm -f /tmp/backend_response.txt /tmp/integration_response.txt
```

---

### Features:

1. **Retries failed checks** up to `MAX_RETRIES` times.
2. **Waits** `SLEEP_INTERVAL` seconds between attempts.
3. **Detailed logs** showing attempt number and response.
4. **Integration check** ensures frontend can talk to backend.

---

### Usage:

```bash
chmod +x verify-deployment.sh
./verify-deployment.sh
```

---
