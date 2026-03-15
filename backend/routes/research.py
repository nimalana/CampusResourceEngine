from fastapi import APIRouter, HTTPException
from cache import cache_get, cache_set
from database import get_resource, list_resources

router = APIRouter(prefix="/research", tags=["research"])


@router.get("")
def list_research():
    cache_key = "list:research"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    items, shard_counts = list_resources("research")
    payload = {
        "data": items,
        "count": len(items),
        "shard_distribution": shard_counts,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload


@router.get("/{project_id}")
def get_research(project_id: str):
    cache_key = f"research:{project_id}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    item, shard, replicas = get_resource("research", project_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Research project '{project_id}' not found")

    payload = {
        "data": item,
        "shard": shard,
        "replicas": replicas,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload
