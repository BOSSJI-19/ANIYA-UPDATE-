# Base Image
FROM python:3.10-slim-bookworm

# Settings
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# --- INSTALL NODE.JS & FFMPEG ---
# Ye Node.js 18 aur FFmpeg install karega
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get install -y ffmpeg git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- REQUIREMENTS ---
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# --- COPY CODE & START ---
COPY . .
CMD ["python", "main.py"]

