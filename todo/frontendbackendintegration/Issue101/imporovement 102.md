ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -I http://dpy3jeqrdnvsx.cloudfront.net
HTTP/1.1 301 Moved Permanently
Server: CloudFront
Date: Sat, 20 Sep 2025 23:15:18 GMT
Content-Type: text/html
Content-Length: 167
Connection: keep-alive
Location: https://dpy3jeqrdnvsx.cloudfront.net/
X-Cache: Redirect from cloudfront
Via: 1.1 a10cec448fae641ceeeb2e78be14b3ba.cloudfront.net (CloudFront)
X-Amz-Cf-Pop: ORD58-P9
X-Amz-Cf-Id: R2H_Y-ij3LeluX2wgyLPIxRdR3ID5B23JoIMgtsm1sJWbhO5BvtPEQ==

ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -IL http://dpy3jeqrdnvsx.cloudfront.net
HTTP/1.1 301 Moved Permanently
Server: CloudFront
Date: Sat, 20 Sep 2025 23:16:19 GMT
Content-Type: text/html
Content-Length: 167
Connection: keep-alive
Location: https://dpy3jeqrdnvsx.cloudfront.net/
X-Cache: Redirect from cloudfront
Via: 1.1 d001ee82d54e86bc2401900221a7c6cc.cloudfront.net (CloudFront)
X-Amz-Cf-Pop: ORD58-P9
X-Amz-Cf-Id: C1xY-Oql5XcgpuzXxNKUaNjCsKLR79okIVchG9fJrfgGZHL7gm0GlQ==

HTTP/2 200 
content-type: text/html
content-length: 6235
date: Sat, 20 Sep 2025 22:19:32 GMT
last-modified: Wed, 10 Sep 2025 05:38:11 GMT
etag: "f4ce3e1962d7b8a0300fce7ffe05bd43"
x-amz-server-side-encryption: AES256
accept-ranges: bytes
server: AmazonS3
x-cache: Hit from cloudfront
via: 1.1 1c8fc3ee57dbb1a10649d90a943a2c6c.cloudfront.net (CloudFront)
x-amz-cf-pop: ORD58-P9
x-amz-cf-id: OjF0Gg7SzzLHvEoPFO9eF2f2PaUBjmBSqf8HEzlCX83vS-6z6Y9vvw==
age: 3408

That’s a textbook successful redirect + secure response 🎉
Let’s unpack the curl -IL output:

Step 1 → HTTP request
HTTP/1.1 301 Moved Permanently
Location: https://dpy3jeqrdnvsx.cloudfront.net/
X-Cache: Redirect from cloudfront
CloudFront immediately redirected your HTTP request to HTTPS.
The Location header confirms the new target.
X-Cache: Redirect from cloudfront means the redirect happened at the edge (not your S3 bucket).
Step 2 → HTTPS request
HTTP/2 200
content-type: text/html
content-length: 6235
server: AmazonS3
x-cache: Hit from cloudfront
Now CloudFront fetched content from the S3 origin (that’s why you see server: AmazonS3).
x-cache: Hit from cloudfront means the object was already cached at the edge → fast load.
HTTP/2 shows the client negotiated a modern, secure protocol.
✅ Net result:
HTTP → HTTPS redirect is fixed
HTTPS content is being served
CloudFront caching is working
What you can do next
Add this check into your deployment verification script so it automatically fails if HTTP doesn’t redirect to HTTPS.
Test your custom domain (if any) in the same way, not just the CloudFront URL.
Optionally set up CloudFront cache invalidations if you deploy new frontend assets and need them refreshed quickly.
Do you want me to update your verification script so it validates the 301 → 200 chain automatically?