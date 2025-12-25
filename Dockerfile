# 1. Naya aur Stable Python Version (Debian 12 Bookworm)
# Ye "buster" wala error fix karega
FROM python:3.10-slim-bookworm

# 2. Logs dekhne ke liye setting
ENV PYTHONUNBUFFERED=1

# 3. Folder set karo
WORKDIR /app

# 4. System Tools Install (FFmpeg Zaroori hai)
# 'bookworm' use karne se apt-get update ka error nahi aayega
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Requirements Install
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 6. Saara Code Copy karo
COPY . .

# 7. Bot Start Command
# Tumhare paas 'start' bash script nahi hai, isliye direct python run karenge
CMD ["python", "main.py"]

