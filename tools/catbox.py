import aiohttp
import os
import aiofiles  # pip install aiofiles

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Fake Browser Headers (Block hone se bachane ke liye)
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
    if not url:
        raise ValueError("URL is missing")
        
    filename = url.split("/")[-1]
    path = os.path.join(DOWNLOAD_DIR, filename)

    # 1. Check Cache (Agar pehle se hai to wapas download mat karo)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path

    timeout = aiohttp.ClientTimeout(total=600) # 10 Minute timeout safe side

    try:
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"Catbox Download Failed: {resp.status}")

                # 2. Async Write (Bot hang nahi hoga)
                async with aiofiles.open(path, mode="wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024): # 1MB Chunks
                        await f.write(chunk)
                        
        return path
        
    except Exception as e:
        # Agar download fail hua aur adhi file ban gayi, to usko delete kar do
        if os.path.exists(path):
            os.remove(path)
        raise e
            
