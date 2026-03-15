from fastapi import APIRouter, Query
from cache import cache_get, cache_set
from database import search_all

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=1, description="Search query")):
    cache_key = f"search:{q.lower().strip()}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    results = search_all(q)
    payload = {
        "query": q,
        "results": results,
        "count": len(results),
        "cache_hit": False,
    }
    cache_set(cache_key, payload, ttl=60)  # shorter TTL for search results
    return payload
