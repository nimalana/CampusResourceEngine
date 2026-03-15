from fastapi import APIRouter, HTTPException
from cache import cache_get, cache_set
from database import get_resource, list_resources

router = APIRouter(prefix="/dining", tags=["dining"])


@router.get("")
def list_dining():
    cache_key = "list:dining"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    items, shard_counts = list_resources("dining")
    payload = {
        "data": items,
        "count": len(items),
        "shard_distribution": shard_counts,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload


@router.get("/{location_id}")
def get_dining(location_id: str):
    cache_key = f"dining:{location_id}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    item, shard, replicas = get_resource("dining", location_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Dining location '{location_id}' not found")

    payload = {
        "data": item,
        "shard": shard,
        "replicas": replicas,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload
