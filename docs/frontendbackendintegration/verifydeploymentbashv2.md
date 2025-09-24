Here’s a **Bash version** of the frontend-backend verification script. You can run it directly in your terminal with `bash verify-deployment.sh`.

```bash
#!/bin/bash

FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
BACKEND_URL="http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com"

echo "🔎 Checking Frontend..."
HTTP_STATUS_FRONTEND=$(curl -o /dev/null -s -w "%{http_code}\n" $FRONTEND_URL)
if [ "$HTTP_STATUS_FRONTEND" -eq 200 ]; then
    echo "✅ Frontend reachable: $HTTP_STATUS_FRONTEND"
else
    echo "❌ Frontend error: $HTTP_STATUS_FRONTEND"
fi

echo -e "\n🔎 Checking Backend Health..."
BACKEND_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/backend_response.txt $BACKEND_URL/health)
HTTP_BODY=$(cat /tmp/backend_response.txt)
if [ "$BACKEND_RESPONSE" -eq 200 ]; then
    echo "✅ Backend reachable: $BACKEND_RESPONSE, response: $HTTP_BODY"
else
    echo "❌ Backend error: $BACKEND_RESPONSE, response: $HTTP_BODY"
fi

echo -e "\n🔎 Checking Frontend-Backend Integration..."
# Replace /api/test with a real API path your frontend exposes that calls the backend
INTEGRATION_STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL/api/test)
INTEGRATION_BODY=$(cat /tmp/integration_response.txt)
if [ "$INTEGRATION_STATUS" -eq 200 ]; then
    echo "✅ Integration OK: $INTEGRATION_STATUS, response: $INTEGRATION_BODY"
else
    echo "❌ Integration error: $INTEGRATION_STATUS, response: $INTEGRATION_BODY"
fi

# Clean up temp files
rm -f /tmp/backend_response.txt /tmp/integration_response.txt
```

### How to use:

1. Save it as `verify-deployment.sh`.
2. Make it executable:

   ```bash
   chmod +x verify-deployment.sh
   ```
3. Run it:

   ```bash
   ./verify-deployment.sh
   ```

It will automatically:

* Check your **frontend URL**.
* Check **backend health**.
* Test **frontend-backend integration** via a sample API endpoint.

