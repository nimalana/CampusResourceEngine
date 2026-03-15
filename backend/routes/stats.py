from fastapi import APIRouter
from cache import get_cache_stats
from database import get_shard_distribution
from consistent_hash import ring

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats():
    cache_stats = get_cache_stats()
    ring_state = ring.get_ring_state()
    shard_dist = get_shard_distribution()

    return {
        "cache": cache_stats,
        "ring": {
            **ring_state,
            # Omit full vnode list from stats summary to keep payload small
            "vnodes": ring_state["vnodes"][:20],  # first 20 for preview
        },
        "shards": {
            "distribution": shard_dist,
            "total_records": sum(shard_dist.values()),
        },
        "replication": {
            "factor": 2,
            "strategy": "consistent-hash-replica",
        },
    }


@router.get("/ring")
def get_ring():
    """Full ring state for frontend visualization (all virtual nodes)."""
    ring_state = ring.get_ring_state()
    shard_dist = get_shard_distribution()
    return {
        **ring_state,
        "shard_record_counts": shard_dist,
    }
