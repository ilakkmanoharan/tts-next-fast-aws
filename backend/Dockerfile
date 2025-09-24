# ------------------- Base image -------------------
FROM python:3.12-slim

# ------------------- Set working directory -------------------
WORKDIR /app

# ------------------- Install dependencies -------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------- Copy app code -------------------
COPY . .

# ------------------- Create log directory -------------------
# Create /var/log/tts-backend and give full access
RUN mkdir -p /var/log/tts-backend && chmod 777 /var/log/tts-backend

# ------------------- (Optional) Create non-root user -------------------
# safer than running as root in production
# RUN useradd -m appuser
# RUN chown -R appuser:appuser /app /var/log/tts-backend
# USER appuser

# ------------------- Expose port -------------------
EXPOSE 8000

# ------------------- Run FastAPI -------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

