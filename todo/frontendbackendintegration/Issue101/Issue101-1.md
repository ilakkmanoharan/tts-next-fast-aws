# Fixing the **HTTP → HTTPS** redirect for your CloudFront distribution — step-by-step

Short answer: make sure the **Viewer Protocol Policy** for the cache behavior(s) that match your requests is set to **“Redirect HTTP to HTTPS”**, save the distribution, and confirm you edited the *behavior that actually matches* the request (cache behaviors are matched in order). If your origin is an S3 *website* endpoint, also check the S3 website settings (website endpoints don’t support HTTPS). ([AWS Documentation][1])

Below is a practical, ordered checklist with console steps, CLI/script examples you can copy-paste, test commands, and troubleshooting tips.

---

## 1) Quick explanation of what went wrong

If `http://dpy3jeqrdnvsx.cloudfront.net` returns **200** instead of **301/308**, one of these is usually true:

* The distribution’s *Viewer Protocol Policy* for the matching cache behavior is still set to allow HTTP (e.g., **Allow HTTP and HTTPS**), not **Redirect HTTP to HTTPS**. ([AWS Documentation][1])
* You edited a behavior that doesn’t match the request path — CloudFront picks the *first* cache behavior whose path pattern matches; the Default (`*`) is evaluated last. ([AWS Documentation][2])
* You are actually hitting the S3 website endpoint or another origin directly (S3 website endpoints serve HTTP and don’t support HTTPS). ([AWS Documentation][3])

---

## 2) Console (GUI) fix — exact clicks

1. Sign in to the AWS Management Console → **CloudFront**. ([AWS Documentation][1])
2. Click the distribution whose DomainName is `dpy3jeqrdnvsx.cloudfront.net`.
3. Open the **Behaviors** tab.
4. Find the **cache behavior** that will match the path you tested (usually the **Default (\*)** behavior unless you have a more specific path). Remember: CloudFront tests behaviors in list order; the first matching pattern wins. ([AWS Documentation][2])
5. Select the behavior → **Edit** → set **Viewer protocol policy** to **Redirect HTTP to HTTPS** (console label) — which is `redirect-to-https` in the API. Save. ([AWS Documentation][1])
6. Wait for the distribution to deploy (Status shows **In Progress** → **Deployed**). Changes must finish deploying to edge locations.
7. Test with curl (see Testing section below).

**Notes:**

* If you have multiple behaviors (API routes, assets, etc.), repeat step 5 for each behavior you want to force to HTTPS. ([AWS Documentation][4])

---

## 3) CLI / script way (copy-paste)

This example shows how to find the distribution ID by domain, pull the config, change ViewerProtocolPolicy, and update the distribution. It uses `jq` for JSON editing.

```bash
# 1) find distribution id (replace domain)
DNAME="dpy3jeqrdnvsx.cloudfront.net"
DIST_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?DomainName=='${DNAME}'].Id | [0]" --output text)

# 2) download current config (this returns JSON containing ETag + DistributionConfig)
aws cloudfront get-distribution-config --id $DIST_ID > dist-config.json

# 3) capture ETag (required by update-distribution)
ETAG=$(jq -r '.ETag' dist-config.json)

# 4) extract DistributionConfig to a separate file
jq '.DistributionConfig' dist-config.json > distribution-config.json

# 5) update ViewerProtocolPolicy in default and any CacheBehaviors (example)
jq '
  .DefaultCacheBehavior.ViewerProtocolPolicy = "redirect-to-https"
  | if .CacheBehaviors and .CacheBehaviors.Items then
      .CacheBehaviors.Items = (.CacheBehaviors.Items | map(.ViewerProtocolPolicy = "redirect-to-https"))
    else .
    end
' distribution-config.json > updated-config.json

# 6) submit the update
aws cloudfront update-distribution \
  --id $DIST_ID \
  --if-match "$ETAG" \
  --distribution-config file://updated-config.json
```

Important: `update-distribution` must be supplied the *entire* `DistributionConfig` JSON and the current `ETag` (`--if-match`). See AWS docs on the get/update flow. ([AWS Documentation][5])

---

## 4) How to test (quick)

Run these from your terminal:

* Check just response headers (expect a **301** and `Location:` header):

```bash
curl -I http://dpy3jeqrdnvsx.cloudfront.net
```

Expected important lines (example):

```
HTTP/1.1 301 Moved Permanently
Location: https://dpy3jeqrdnvsx.cloudfront.net/
x-cache: Redirect from CloudFront
```

* Follow redirects to confirm content served over HTTPS:

```bash
curl -IL http://dpy3jeqrdnvsx.cloudfront.net
```

If you still see `HTTP/1.1 200 OK` for an HTTP request, re-check the behavior settings and ordering. ([AWS Documentation][1])

---

## 5) If your origin is an S3 website endpoint

S3 *website endpoints* (`bucket.s3-website-<region>.amazonaws.com`) **do not support HTTPS**. You can still have CloudFront perform the HTTPS redirect at the viewer — but if you want CloudFront → origin to use HTTPS, the recommended approach is to use the S3 *REST API endpoint* (the normal bucket endpoint) or enable OAC/OAI, not the website endpoint. If you rely on S3 website redirect rules, inspect those too (they can produce redirects themselves). ([AWS Documentation][3])

---

## 6) Common troubleshooting checklist

* ✅ **Are you editing the behavior that actually matches your path?** (Cache behaviors are matched in order; default `*` is last.) ([AWS Documentation][2])
* ✅ **Did you save and wait for "Deployed"?** CloudFront changes take a few minutes to propagate.
* ✅ **Did you test the CloudFront domain directly (not the S3 domain)?** Make sure DNS is pointing to CloudFront (Route 53 alias/DDNS) and not directly to S3.
* ✅ **If you changed config but still see old behavior, create an invalidation for the object(s)** — especially if you were debugging content responses; invalidations remove cached content from edge caches. (Note: changing viewer protocol policy is a config change and should not *require* invalidation, but if you saw cached responses it can help.) ([AWS Documentation][6])
* ✅ **Check HTTP methods**: CloudFront does **not** redirect `POST/PUT/DELETE/OPTIONS/PATCH` from HTTP → HTTPS; those get a 403 if viewer policy is redirect. (Only `GET` and `HEAD` are auto-redirected.) ([AWS Documentation][4])
* ✅ **Multiple distributions?** Verify the domain maps to the distribution you edited (`aws cloudfront list-distributions` and check `DomainName`/`Aliases`). ([AWS Documentation][7])

---

## 7) Useful AWS docs I referenced

* How to require HTTPS (Viewer Protocol Policy) — CloudFront Developer Guide. ([AWS Documentation][1])
* CloudFront returns 301 when redirecting HTTP → HTTPS. ([AWS Documentation][1])
* S3 website endpoints do **not** support HTTPS (and alternatives). ([AWS Documentation][3])
* Cache behaviors path pattern & order (first match wins, default `*` last). ([AWS Documentation][2])
* Invalidation doc (how to clear edge caches). ([AWS Documentation][6])

---

If you want, I can:

* generate the exact `jq` edit + `aws` commands for your distribution if you paste the *distribution ID* (not the domain), or
* walk you through the Console clicks and the precise behavior to edit for your setup.

Which would you like me to do next?

[1]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https-viewers-to-cloudfront.html?utm_source=chatgpt.com "Require HTTPS for communication between viewers and ..."
[2]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesCacheBehavior.html?utm_source=chatgpt.com "Cache behavior settings - Amazon CloudFront"
[3]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteEndpoints.html?utm_source=chatgpt.com "Website endpoints - Amazon Simple Storage Service"
[4]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https-cloudfront-to-s3-origin.html?utm_source=chatgpt.com "Require HTTPS for communication between CloudFront and ..."
[5]: https://docs.aws.amazon.com/cli/latest/reference/cloudfront/update-distribution.html?utm_source=chatgpt.com "update-distribution — AWS CLI 2.30.5 Command Reference"
[6]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html?utm_source=chatgpt.com "Invalidate files to remove content - Amazon CloudFront"
[7]: https://docs.aws.amazon.com/cli/latest/reference/cloudfront/get-distribution.html?utm_source=chatgpt.com "get-distribution — AWS CLI 2.30.5 Command Reference"

Next step: We can:
generate the exact jq edit + aws commands for your distribution if you paste the distribution ID (not the domain), or
walk you through the Console clicks and the precise behavior to edit for your setup.
