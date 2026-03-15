from fastapi import APIRouter, HTTPException
from cache import cache_get, cache_set
from database import get_resource, list_resources

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events():
    cache_key = "list:events"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    items, shard_counts = list_resources("event")
    payload = {
        "data": items,
        "count": len(items),
        "shard_distribution": shard_counts,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload


@router.get("/{event_id}")
def get_event(event_id: str):
    cache_key = f"event:{event_id}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    item, shard, replicas = get_resource("event", event_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")

    payload = {
        "data": item,
        "shard": shard,
        "replicas": replicas,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload
