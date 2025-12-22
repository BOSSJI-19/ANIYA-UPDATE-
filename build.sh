#!/usr/bin/env bash
# build.sh

# Install system dependencies for RENDER
apt-get update
apt-get install -y ffmpeg python3-pip

# Install Python packages
pip install -r requirements.txt

# Pyrogram session generate (if needed)
python3 -c "from pyrogram import Client; import asyncio; asyncio.run(Client('music_assistant').start())" || true