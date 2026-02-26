# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies (Postgres + OpenCV + MediaPipe)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    cmake \
    postgresql-client \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default command (will be overridden by docker-compose)
CMD ["python", "main.py"]