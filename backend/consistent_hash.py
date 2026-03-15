import hashlib
import bisect
import math
from typing import List, Dict, Optional


class ConsistentHashRing:
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes = list(nodes)
        for node in nodes:
            self._add_node_to_ring(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def _add_node_to_ring(self, node: str):
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}:vnode:{i}"
            hash_val = self._hash(vnode_key)
            self.ring[hash_val] = node
            bisect.insort(self.sorted_keys, hash_val)

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise RuntimeError("Hash ring is empty")
        hash_val = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

    def get_replicas(self, key: str, n: int = 2) -> List[str]:
        if not self.ring:
            return []
        hash_val = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        replicas = []
        seen = set()
        total = len(self.sorted_keys)
        for i in range(total):
            node = self.ring[self.sorted_keys[(idx + i) % total]]
            if node not in seen:
                replicas.append(node)
                seen.add(node)
            if len(replicas) == n:
                break
        return replicas

    def get_ring_state(self) -> dict:
        """Return ring state suitable for frontend visualization."""
        max_val = 2**32
        vnodes_by_node: Dict[str, List[dict]] = {n: [] for n in self.nodes}

        for i, hash_val in enumerate(self.sorted_keys):
            node = self.ring[hash_val]
            # normalize position to 0-1 for angle computation
            angle = (hash_val / max_val) * 2 * math.pi
            vnodes_by_node[node].append({
                "position": hash_val,
                "angle_deg": round((hash_val / max_val) * 360, 2),
            })

        node_counts = {n: len(v) for n, v in vnodes_by_node.items()}
        total_vnodes = len(self.sorted_keys)

        return {
            "nodes": self.nodes,
            "virtual_nodes_per_node": self.virtual_nodes,
            "total_virtual_nodes": total_vnodes,
            "node_distribution": {
                n: {
                    "count": node_counts[n],
                    "percentage": round(node_counts[n] / total_vnodes * 100, 2),
                }
                for n in self.nodes
            },
            "vnodes": [
                {
                    "position": self.ring[k],
                    "hash": self.sorted_keys[i],
                    "angle_deg": round((self.sorted_keys[i] / max_val) * 360, 2),
                }
                for i, k in enumerate(self.sorted_keys)
            ],
        }


# Singleton instance with 4 shards × 150 virtual nodes = 600 total vnodes
SHARD_NAMES = ["shard-1", "shard-2", "shard-3", "shard-4"]
ring = ConsistentHashRing(nodes=SHARD_NAMES, virtual_nodes=150)
