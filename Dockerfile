# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    scrot \
    xclip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    rich \
    pydantic \
    python-dotenv \
    google-genai \
    chromadb \
    networkx \
    pystray \
    pillow

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data logs voice/models

# Default command — text mode
CMD ["python", "sprout.py"]