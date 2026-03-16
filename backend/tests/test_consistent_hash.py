"""
Tests for consistent hashing — pure logic, no DB or network required.
"""

import pytest
from consistent_hash import ConsistentHashRing, SHARD_NAMES, ring


class TestRingConfiguration:
    def test_four_shards(self):
        assert len(ring.nodes) == 4

    def test_shard_names(self):
        assert set(ring.nodes) == {"shard-1", "shard-2", "shard-3", "shard-4"}

    def test_total_virtual_nodes(self):
        # 4 shards × 150 vnodes = 600
        assert len(ring.sorted_keys) == 600

    def test_each_shard_has_150_vnodes(self):
        counts = {}
        for hash_val in ring.sorted_keys:
            node = ring.ring[hash_val]
            counts[node] = counts.get(node, 0) + 1
        for shard in SHARD_NAMES:
            assert counts[shard] == 150


class TestNodeLookup:
    def test_get_node_returns_valid_shard(self):
        assert ring.get_node("comp110") in SHARD_NAMES

    def test_get_node_is_deterministic(self):
        key = "course:comp110"
        assert ring.get_node(key) == ring.get_node(key)

    def test_different_keys_can_map_to_different_shards(self):
        keys = [f"resource:{i}" for i in range(50)]
        shards = {ring.get_node(k) for k in keys}
        # With 50 keys across 4 shards we should see at least 2 distinct shards
        assert len(shards) >= 2

    def test_empty_ring_raises(self):
        empty = ConsistentHashRing(nodes=[], virtual_nodes=10)
        with pytest.raises(RuntimeError):
            empty.get_node("any_key")


class TestReplicas:
    def test_replica_count_is_two(self):
        replicas = ring.get_replicas("course:comp110", n=2)
        assert len(replicas) == 2

    def test_replicas_are_unique_shards(self):
        replicas = ring.get_replicas("course:comp110", n=2)
        assert len(set(replicas)) == 2

    def test_replicas_are_valid_shard_names(self):
        for r in ring.get_replicas("dining:lenoir", n=2):
            assert r in SHARD_NAMES

    def test_primary_is_first_replica(self):
        key = "club:cs-club"
        primary = ring.get_node(key)
        replicas = ring.get_replicas(key, n=2)
        assert replicas[0] == primary

    def test_single_node_ring_returns_one_replica(self):
        tiny = ConsistentHashRing(nodes=["only-shard"], virtual_nodes=5)
        replicas = tiny.get_replicas("any-key", n=2)
        assert replicas == ["only-shard"]


class TestRingState:
    def test_ring_state_keys(self):
        state = ring.get_ring_state()
        assert "nodes" in state
        assert "virtual_nodes_per_node" in state
        assert "total_virtual_nodes" in state
        assert "node_distribution" in state
        assert "vnodes" in state

    def test_ring_state_vnode_count(self):
        state = ring.get_ring_state()
        assert state["total_virtual_nodes"] == 600
        assert state["virtual_nodes_per_node"] == 150

    def test_ring_state_percentages_sum_to_100(self):
        state = ring.get_ring_state()
        total_pct = sum(
            v["percentage"] for v in state["node_distribution"].values()
        )
        assert abs(total_pct - 100.0) < 0.5  # allow rounding error

    def test_vnode_angle_in_range(self):
        state = ring.get_ring_state()
        for vnode in state["vnodes"]:
            assert 0.0 <= vnode["angle_deg"] < 360.0


class TestSchemaNameConversion:
    """Verify the shard→schema name helper used by database.py."""

    def test_hyphen_to_underscore(self):
        from database import _schema
        assert _schema("shard-1") == "shard_1"
        assert _schema("shard-4") == "shard_4"

    def test_all_shard_names_convert(self):
        from database import _schema
        for shard in SHARD_NAMES:
            schema = _schema(shard)
            assert "-" not in schema
            assert schema.startswith("shard_")
