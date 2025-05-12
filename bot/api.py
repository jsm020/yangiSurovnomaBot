# ──────────────── api.py ────────────────
import aiohttp
from utils import safe_json
from config import DJANGO_API_URL, SURVEY_API_URL
from datetime import datetime, timezone


async def post_json(url, payload):
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=payload) as r:
            return r.status, await safe_json(r)

async def patch_json(url, payload):
    async with aiohttp.ClientSession() as s:
        async with s.patch(url, json=payload) as r:
            return r.status, await safe_json(r)

async def get_json(url):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return r.status, await safe_json(r)

async def finish_participation(part_id):
    return await patch_json(f"{SURVEY_API_URL}{part_id}/")