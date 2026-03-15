from fastapi import APIRouter, HTTPException
from cache import cache_get, cache_set
from database import get_resource, list_resources
from consistent_hash import ring

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
def list_courses():
    cache_key = "list:courses"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    items, shard_counts = list_resources("course")
    payload = {
        "data": items,
        "count": len(items),
        "shard_distribution": shard_counts,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload


@router.get("/{course_id}")
def get_course(course_id: str):
    cache_key = f"course:{course_id}"
    cached, hit = cache_get(cache_key)
    if hit:
        return {**cached, "cache_hit": True}

    item, shard, replicas = get_resource("course", course_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")

    payload = {
        "data": item,
        "shard": shard,
        "replicas": replicas,
        "cache_hit": False,
    }
    cache_set(cache_key, payload)
    return payload
