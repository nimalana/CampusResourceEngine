"""
In-memory sharded database using consistent hashing.

Each resource is assigned to a shard via the hash ring.
Write operations use 2-replica writes; reads include read-repair.
"""

from typing import Any, Dict, List, Optional, Tuple
from consistent_hash import ring, SHARD_NAMES
from seed_data import COURSES, CLUBS, RESEARCH, EVENTS, DINING

# Each shard holds a dict keyed by resource_id
_shards: Dict[str, Dict[str, Any]] = {name: {} for name in SHARD_NAMES}
# Shard write timestamps for read-repair
_shard_timestamps: Dict[str, Dict[str, float]] = {name: {} for name in SHARD_NAMES}

import time as _time


def _put(resource_id: str, value: Any) -> List[str]:
    """Write to primary + one replica (2-replica write). Returns list of written shards."""
    replicas = ring.get_replicas(resource_id, n=2)
    ts = _time.time()
    for shard in replicas:
        _shards[shard][resource_id] = value
        _shard_timestamps[shard][resource_id] = ts
    return replicas


def _get(resource_id: str) -> Tuple[Optional[Any], str]:
    """
    Read from primary shard.
    Performs read-repair if a replica has a newer timestamp.
    Returns (value, shard_name).
    """
    primary = ring.get_node(resource_id)
    replicas = ring.get_replicas(resource_id, n=2)

    value = _shards[primary].get(resource_id)
    primary_ts = _shard_timestamps[primary].get(resource_id, 0)

    # Read-repair: scan replicas for fresher data
    for shard in replicas:
        shard_ts = _shard_timestamps[shard].get(resource_id, 0)
        if shard_ts > primary_ts and resource_id in _shards[shard]:
            # Repair primary with fresher replica data
            _shards[primary][resource_id] = _shards[shard][resource_id]
            _shard_timestamps[primary][resource_id] = shard_ts
            value = _shards[primary][resource_id]
            primary_ts = shard_ts

    return value, primary


def _list_by_type(resource_type: str) -> Tuple[List[Any], Dict[str, int]]:
    """List all resources of a given type. Returns (items, shard_counts)."""
    items = []
    shard_counts: Dict[str, int] = {s: 0 for s in SHARD_NAMES}
    for shard, store in _shards.items():
        for key, val in store.items():
            if key.startswith(f"{resource_type}:"):
                items.append(val)
                shard_counts[shard] += 1
    # De-duplicate (a key may live in 2 shards via replication)
    seen_ids = set()
    unique = []
    for item in items:
        item_id = item.get("id", "")
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            unique.append(item)
    return unique, shard_counts


def _seed(resource_type: str, items: List[dict]):
    for item in items:
        _put(f"{resource_type}:{item['id']}", item)


# Seed on import
_seed("course", COURSES)
_seed("club", CLUBS)
_seed("research", RESEARCH)
_seed("event", EVENTS)
_seed("dining", DINING)


# ── Public API ──────────────────────────────────────────────────────────────

def get_resource(resource_type: str, resource_id: str) -> Tuple[Optional[dict], str, List[str]]:
    """Returns (item, primary_shard, replica_shards)."""
    key = f"{resource_type}:{resource_id}"
    value, primary = _get(key)
    replicas = ring.get_replicas(key, n=2)
    return value, primary, replicas


def list_resources(resource_type: str) -> Tuple[List[dict], Dict[str, int]]:
    return _list_by_type(resource_type)


def search_all(query: str) -> List[dict]:
    query_lower = query.lower()
    results = []
    seen_ids = set()
    for resource_type in ["course", "club", "research", "event", "dining"]:
        items, _ = _list_by_type(resource_type)
        for item in items:
            item_id = item.get("id", "")
            if item_id in seen_ids:
                continue
            text = " ".join(str(v) for v in item.values()).lower()
            if query_lower in text:
                seen_ids.add(item_id)
                results.append({"type": resource_type, **item})
    return results


def get_shard_distribution() -> Dict[str, int]:
    return {shard: len(store) for shard, store in _shards.items()}
