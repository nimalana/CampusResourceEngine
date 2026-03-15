from fastapi import APIRouter, HTTPException
from cache import cache_get, cache_set
from database import get_resource, list_resources

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get("")
def list_clubs():
    cache_key = "list:clubs"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    items, shard_counts = list_resources("club")
    payload = {
        "data": items,
        "count": len(items),
        "shard_distribution": shard_counts,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload


@router.get("/{club_id}")
def get_club(club_id: str):
    cache_key = f"club:{club_id}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    item, shard, replicas = get_resource("club", club_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Club '{club_id}' not found")

    payload = {
        "data": item,
        "shard": shard,
        "replicas": replicas,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload
