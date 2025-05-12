# ──────────────── utils.py ────────────────
import aiohttp

async def safe_json(resp):
    try:
        return await resp.json()
    except aiohttp.ContentTypeError:
        return {}

async def json_count(data):
    if not isinstance(data, (dict, list)):
        return 0
    if isinstance(data, dict):
        return data.get("count", 0)
    return len(data)  # list bo‘lsa
