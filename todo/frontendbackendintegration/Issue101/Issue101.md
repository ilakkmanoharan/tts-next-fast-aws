HTTP → HTTPS redirect check failed
The script tried http://dpy3jeqrdnvsx.cloudfront.net and got status 200 instead of a 301/308.
That means your CloudFront distribution (or S3 bucket if it’s the origin) is serving content directly on HTTP without forcing a redirect to HTTPS.
Fix:
In the CloudFront distribution settings → Behaviors, make sure Viewer Protocol Policy is set to Redirect HTTP to HTTPS.
If you’re using an S3 static site, also check that your bucket policy and settings are not allowing direct HTTP access without redirection.