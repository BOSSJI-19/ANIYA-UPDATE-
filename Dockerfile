# Base Image: Python 3.10 (Stable Version)
FROM python:3.10-slim-bullseye

# Folder Setup
WORKDIR /app

# 1. System Updates & Basic Tools
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    gnupg \
    unzip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 20 (Manual Method)
# Ye method ensure karta hai ki 'node' command har jagah available ho
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# 3. Python Requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. Copy Code & Start
COPY . .
CMD ["python", "main.py"]

