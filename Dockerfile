# Simplified Dockerfile for OpenUser
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.docker.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY pyproject.toml README.md ./

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OPENUSER_ENV=production \
    OPENUSER_API_HOST=0.0.0.0 \
    OPENUSER_API_PORT=8000

# Create directories for data persistence
RUN mkdir -p /app/data /app/models /app/cache /app/uploads && \
    chmod -R 755 /app/data /app/models /app/cache /app/uploads

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Run API server with uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
