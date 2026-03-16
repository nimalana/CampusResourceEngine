"""
Tests for the cache module — uses the in-memory fallback so no Redis needed.
"""

import pytest
import cache as cache_module


@pytest.fixture(autouse=True)
def reset_cache():
    """Wipe cache state before every test."""
    cache_module._memory_cache.clear()
    cache_module._hits = 0
    cache_module._misses = 0
    # Force memory-fallback mode regardless of whether Redis is running
    cache_module.REDIS_AVAILABLE = False
    yield
    cache_module._memory_cache.clear()
    cache_module._hits = 0
    cache_module._misses = 0


class TestCacheMissAndHit:
    def test_miss_on_empty_cache(self):
        val, hit = cache_module.cache_get("missing")
        assert val is None
        assert hit is False

    def test_set_then_get_returns_hit(self):
        cache_module.cache_set("k", {"foo": "bar"})
        val, hit = cache_module.cache_get("k")
        assert hit is True
        assert val == {"foo": "bar"}

    def test_set_preserves_various_types(self):
        cache_module.cache_set("num", 42)
        cache_module.cache_set("lst", [1, 2, 3])
        cache_module.cache_set("nested", {"a": {"b": True}})

        assert cache_module.cache_get("num")[0] == 42
        assert cache_module.cache_get("lst")[0] == [1, 2, 3]
        assert cache_module.cache_get("nested")[0] == {"a": {"b": True}}


class TestMetrics:
    def test_miss_increments_miss_counter(self):
        cache_module.cache_get("nope")
        assert cache_module._misses == 1
        assert cache_module._hits == 0

    def test_hit_increments_hit_counter(self):
        cache_module.cache_set("key", "val")
        cache_module.cache_get("key")
        assert cache_module._hits == 1
        assert cache_module._misses == 0

    def test_multiple_hits_and_misses(self):
        cache_module.cache_set("a", 1)
        cache_module.cache_get("a")   # hit
        cache_module.cache_get("a")   # hit
        cache_module.cache_get("b")   # miss
        assert cache_module._hits == 2
        assert cache_module._misses == 1

    def test_hit_rate_calculation(self):
        cache_module.cache_set("x", 1)
        cache_module.cache_get("x")   # hit
        cache_module.cache_get("y")   # miss
        stats = cache_module.get_cache_stats()
        assert stats["hit_rate"] == 0.5
        assert stats["total_requests"] == 2

    def test_hit_rate_zero_when_no_requests(self):
        stats = cache_module.get_cache_stats()
        assert stats["hit_rate"] == 0.0
        assert stats["total_requests"] == 0


class TestDelete:
    def test_delete_removes_entry(self):
        cache_module.cache_set("gone", "value")
        cache_module.cache_delete("gone")
        _, hit = cache_module.cache_get("gone")
        assert hit is False

    def test_delete_nonexistent_key_does_not_raise(self):
        cache_module.cache_delete("never_existed")  # should not raise


class TestCacheStats:
    def test_stats_shape(self):
        stats = cache_module.get_cache_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "total_requests" in stats
        assert "hit_rate" in stats
        assert "redis_available" in stats
        assert "uptime_seconds" in stats

    def test_redis_available_is_false_in_fallback(self):
        stats = cache_module.get_cache_stats()
        assert stats["redis_available"] is False
