"""
Async SQLite TTL cache for API responses.
Keys: "{api_name}:{params_hash}" → JSON value with expiry timestamp.
"""
import json
import time
import hashlib
import aiosqlite
from pathlib import Path
from typing import Any

from config import DB_PATH

_SCHEMA = Path(__file__).parent / "schema.sql"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        schema = _SCHEMA.read_text()
        await db.executescript(schema)
        await db.commit()


def _make_key(api_name: str, params: dict) -> str:
    params_str = json.dumps(params, sort_keys=True)
    h = hashlib.md5(params_str.encode()).hexdigest()[:12]
    return f"{api_name}:{h}"


async def cache_get(api_name: str, params: dict) -> Any | None:
    key = _make_key(api_name, params)
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT value_json FROM api_cache WHERE cache_key = ? AND expires_at > ?",
            (key, now),
        ) as cur:
            row = await cur.fetchone()
    if row:
        return json.loads(row[0])
    return None


async def cache_set(api_name: str, params: dict, value: Any, ttl: int) -> None:
    key = _make_key(api_name, params)
    now = time.time()
    expires = now + ttl
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO api_cache(cache_key, value_json, created_at, expires_at) VALUES (?,?,?,?)",
            (key, json.dumps(value), now, expires),
        )
        await db.commit()


async def cache_prune() -> int:
    """Remove expired entries. Returns count deleted."""
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM api_cache WHERE expires_at <= ?", (now,))
        await db.commit()
        return cur.rowcount


async def cache_stats() -> dict:
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM api_cache") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM api_cache WHERE expires_at > ?", (now,)) as cur:
            live = (await cur.fetchone())[0]
    return {"total_entries": total, "live_entries": live, "expired_entries": total - live}
