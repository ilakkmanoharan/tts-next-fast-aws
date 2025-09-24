
Old version:

@app.get("/health")
async def health_check():
    """
    Health check for ECS. Verifies S3 and Polly are reachable.
    """
    # Check S3
    try:
        s3.head_bucket(Bucket=BUCKET)
    except Exception as e:
        return JSONResponse({"status": "fail", "dependency": "s3", "error": str(e)}, status_code=500)

    # Check Polly
    try:
        polly.describe_voices(MaxResults=1)
    except Exception as e:
        return JSONResponse({"status": "fail", "dependency": "polly", "error": str(e)}, status_code=500)

    return JSONResponse({"status": "ok"})


    New version:


# ------------------- Health Check Endpoint -------------------
@app.get("/health")
async def health_check():
    """
    Health check for ECS. Verifies S3 and Polly are reachable.
    Returns detailed info about what fails.
    """
    status = {"s3": "ok", "polly": "ok"}
    http_status = 200

    # Check S3
    try:
        s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
    except s3.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        status["s3"] = f"fail ({error_code}) - check IAM task role and bucket name"
        http_status = 500

    # Check Polly
    try:
        polly.describe_voices(MaxResults=1)
    except Exception as e:
        status["polly"] = f"fail ({str(e)})"
        http_status = 500

    if http_status == 200:
        return JSONResponse({"status": "ok", "dependencies": status})
    else:
        return JSONResponse({"status": "fail", "dependencies": status}, status_code=http_status)

