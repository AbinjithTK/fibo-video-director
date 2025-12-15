# FIBO Video Director Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add boto3 and httpx for S3 and async HTTP
RUN pip install --no-cache-dir boto3 httpx fal-client

# Copy application code
COPY api_server.py .
COPY fibo_video_director.py .
COPY enhanced_fibo_director.py .
COPY fal_fibo_integration.py .
COPY s3_storage.py .
COPY fibo_integration.py .
COPY start_server.py .

# Create cache directory
RUN mkdir -p cache examples/outputs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the server
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
