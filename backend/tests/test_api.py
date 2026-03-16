"""
API endpoint tests — database calls are mocked so no PostgreSQL is required.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# ── Sample fixture data ───────────────────────────────────────────────────────

MOCK_COURSE = {
    "id": "comp110", "code": "COMP 110",
    "title": "Introduction to Programming and Data Science",
    "department": "Computer Science", "credits": 3,
    "instructor": "Kris Jordan", "description": "Intro to Python.",
    "seats_available": 12, "total_seats": 120,
    "schedule": "MWF 10:10-11:00", "location": "Sitterson Hall 014",
    "tags": ["python", "beginner"],
}

MOCK_CLUB = {
    "id": "cs-club", "name": "Carolina Hackers",
    "category": "Academic / Tech", "description": "Coding meetups.",
    "meeting_schedule": "Thursdays 6:30 PM", "location": "Sitterson Hall 11",
    "president": "Marcus Chen", "email": "carolinahackers@unc.edu",
    "member_count": 320, "founded": 2004, "tags": ["coding", "hackathon"],
}

MOCK_SHARD_COUNTS = {"shard-1": 3, "shard-2": 3, "shard-3": 3, "shard-4": 3}


@pytest.fixture(scope="module")
def client():
    """
    TestClient with db_init and cache patched so no real services are needed.
    """
    with patch("db_init.init_db"), \
         patch("cache.REDIS_AVAILABLE", False):
        import importlib, main as main_module
        with TestClient(main_module.app) as c:
            yield c


# ── Root / health ─────────────────────────────────────────────────────────────

class TestRoot:
    def test_root_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_has_endpoints_list(self, client):
        body = client.get("/").json()
        assert "endpoints" in body
        assert "/courses" in body["endpoints"]

    def test_health_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ── Courses ───────────────────────────────────────────────────────────────────

class TestCoursesEndpoints:
    def test_list_courses_200(self, client):
        with patch("routes.courses.list_resources", return_value=([MOCK_COURSE], MOCK_SHARD_COUNTS)):
            r = client.get("/courses")
        assert r.status_code == 200

    def test_list_courses_response_shape(self, client):
        with patch("routes.courses.list_resources", return_value=([MOCK_COURSE], MOCK_SHARD_COUNTS)):
            body = client.get("/courses").json()
        assert "data" in body
        assert "count" in body
        assert "shard_distribution" in body
        assert body["count"] == 1

    def test_get_course_200(self, client):
        with patch("routes.courses.get_resource", return_value=(MOCK_COURSE, "shard-1", ["shard-1", "shard-2"])):
            r = client.get("/courses/comp110")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == "comp110"

    def test_get_course_has_shard_info(self, client):
        with patch("routes.courses.get_resource", return_value=(MOCK_COURSE, "shard-1", ["shard-1", "shard-2"])):
            body = client.get("/courses/comp110").json()
        assert "shard" in body
        assert "replicas" in body

    def test_get_course_404(self, client):
        with patch("routes.courses.get_resource", return_value=(None, "shard-1", ["shard-1"])):
            r = client.get("/courses/nonexistent")
        assert r.status_code == 404


# ── Clubs ─────────────────────────────────────────────────────────────────────

class TestClubsEndpoints:
    def test_list_clubs_200(self, client):
        with patch("routes.clubs.list_resources", return_value=([MOCK_CLUB], MOCK_SHARD_COUNTS)):
            r = client.get("/clubs")
        assert r.status_code == 200

    def test_get_club_200(self, client):
        with patch("routes.clubs.get_resource", return_value=(MOCK_CLUB, "shard-2", ["shard-2", "shard-3"])):
            r = client.get("/clubs/cs-club")
        assert r.status_code == 200

    def test_get_club_404(self, client):
        with patch("routes.clubs.get_resource", return_value=(None, "shard-1", [])):
            r = client.get("/clubs/fake-club")
        assert r.status_code == 404


# ── Search ────────────────────────────────────────────────────────────────────

class TestSearchEndpoint:
    def test_search_returns_200(self, client):
        with patch("routes.search.search_all", return_value=[{**MOCK_COURSE, "type": "course"}]):
            r = client.get("/search?q=comp")
        assert r.status_code == 200

    def test_search_response_shape(self, client):
        with patch("routes.search.search_all", return_value=[{**MOCK_COURSE, "type": "course"}]):
            body = client.get("/search?q=comp").json()
        assert "query" in body
        assert "results" in body
        assert "count" in body
        assert body["count"] == 1

    def test_search_empty_query_422(self, client):
        r = client.get("/search?q=")
        assert r.status_code == 422

    def test_search_missing_query_422(self, client):
        r = client.get("/search")
        assert r.status_code == 422

    def test_search_no_results(self, client):
        with patch("routes.search.search_all", return_value=[]):
            body = client.get("/search?q=xyznotfound").json()
        assert body["count"] == 0
        assert body["results"] == []


# ── Stats ─────────────────────────────────────────────────────────────────────

class TestStatsEndpoints:
    def test_stats_200(self, client):
        with patch("routes.stats.get_shard_distribution", return_value=MOCK_SHARD_COUNTS):
            r = client.get("/stats")
        assert r.status_code == 200

    def test_stats_response_shape(self, client):
        with patch("routes.stats.get_shard_distribution", return_value=MOCK_SHARD_COUNTS):
            body = client.get("/stats").json()
        assert "cache" in body
        assert "ring" in body
        assert "shards" in body
        assert "replication" in body

    def test_stats_replication_factor(self, client):
        with patch("routes.stats.get_shard_distribution", return_value=MOCK_SHARD_COUNTS):
            body = client.get("/stats").json()
        assert body["replication"]["factor"] == 2

    def test_ring_endpoint_200(self, client):
        with patch("routes.stats.get_shard_distribution", return_value=MOCK_SHARD_COUNTS):
            r = client.get("/stats/ring")
        assert r.status_code == 200

    def test_ring_has_vnodes(self, client):
        with patch("routes.stats.get_shard_distribution", return_value=MOCK_SHARD_COUNTS):
            body = client.get("/stats/ring").json()
        assert "vnodes" in body
        assert len(body["vnodes"]) == 600
