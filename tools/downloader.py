import aiohttp
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://catbox.moe/"
}

async def download_from_catbox(url: str) -> str:
    filename = url.split("/")[-1]
    path = os.path.join(DOWNLOAD_DIR, filename)

    # already downloaded
    if os.path.exists(path):
        return path

    timeout = aiohttp.ClientTimeout(total=300)

    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception("catbox download failed")

            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    f.write(chunk)

    return path
