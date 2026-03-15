"""
Redis cache-aside implementation with graceful in-memory fallback.

Cache-aside pattern:
  1. Check cache → hit: return data + mark hit
  2. Miss: load from source, write to cache, return data + mark miss

Metrics are tracked in-process for the /stats endpoint.
"""

import json
import time
from typing import Any, Optional, Tuple

try:
    import redis

    _redis_client = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=1)
    _redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    _redis_client = None
    REDIS_AVAILABLE = False

# In-memory fallback when Redis is unavailable
_memory_cache: dict[str, Tuple[Any, float]] = {}
_MEMORY_TTL = 300  # seconds

# Global metrics
_hits = 0
_misses = 0
_cache_start_time = time.time()


def _serialize(value: Any) -> str:
    return json.dumps(value)


def _deserialize(raw: str) -> Any:
    return json.loads(raw)


def cache_get(key: str) -> Tuple[Optional[Any], bool]:
    """
    Returns (value, hit).
    value is None on miss. hit is True when served from cache.
    """
    global _hits, _misses

    if REDIS_AVAILABLE:
        try:
            raw = _redis_client.get(key)
            if raw is not None:
                _hits += 1
                return _deserialize(raw), True
        except Exception:
            pass
    else:
        entry = _memory_cache.get(key)
        if entry is not None:
            value, expires_at = entry
            if time.time() < expires_at:
                _hits += 1
                return value, True
            else:
                _memory_cache.pop(key, None)

    _misses += 1
    return None, False


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Write value to cache with TTL (seconds)."""
    if REDIS_AVAILABLE:
        try:
            _redis_client.setex(key, ttl, _serialize(value))
            return
        except Exception:
            pass
    # Fallback
    _memory_cache[key] = (value, time.time() + _MEMORY_TTL)


def cache_delete(key: str) -> None:
    if REDIS_AVAILABLE:
        try:
            _redis_client.delete(key)
        except Exception:
            pass
    _memory_cache.pop(key, None)


def get_cache_stats() -> dict:
    total = _hits + _misses
    return {
        "hits": _hits,
        "misses": _misses,
        "total_requests": total,
        "hit_rate": round(_hits / total, 4) if total > 0 else 0.0,
        "redis_available": REDIS_AVAILABLE,
        "uptime_seconds": round(time.time() - _cache_start_time, 1),
    }
