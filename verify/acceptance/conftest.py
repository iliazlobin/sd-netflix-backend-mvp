"""Shared fixtures and helpers for the Netflix MVP black-box acceptance suite.

These tests do NOT import `src.netflix`. They talk to the running system
via HTTP at API_BASE_URL. Test isolation is achieved through unique
identifiers per test — no database clearing required.
"""

import os
import uuid

import httpx
import pytest

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def base_url():
    return API_BASE_URL


@pytest.fixture(scope="session")
def client(base_url):
    """Session-scoped httpx client for the entire acceptance run."""
    with httpx.Client(base_url=base_url, timeout=30) as c:
        yield c


@pytest.fixture
def fresh_uuid():
    """Unique UUID per test for isolation."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------


def assert_status(r, expected_status):
    """Assert status and return parsed JSON."""
    assert r.status_code == expected_status, (
        f"Expected {expected_status}, got {r.status_code}: {r.text}"
    )
    if r.status_code == 204:
        return None
    return r.json()


def assert_200(r):
    return assert_status(r, 200)


def assert_201(r):
    return assert_status(r, 201)


def assert_204(r):
    return assert_status(r, 204)


def assert_404(r):
    assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"
    return r.json()


def assert_409(r):
    assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"
    return r.json()


def assert_422(r):
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
    return r.json()


# ---------------------------------------------------------------------------
# Setup helpers — create entities via HTTP
# ---------------------------------------------------------------------------


def create_account(client, email=None):
    """Create an account and return the parsed response body (201)."""
    if email is None:
        email = f"user-{uuid.uuid4().hex[:8]}@test.com"
    r = client.post("/api/v1/accounts", json={"email": email})
    return assert_201(r)


def get_account(client, account_id):
    """Fetch an account by id."""
    r = client.get(f"/api/v1/accounts/{account_id}")
    return assert_200(r)


def create_profile(client, account_id, name=None, is_kids=False):
    """Create a profile and return the parsed response body (201)."""
    if name is None:
        name = f"Profile-{uuid.uuid4().hex[:6]}"
    r = client.post(
        "/api/v1/profiles",
        json={"account_id": account_id, "name": name, "is_kids": is_kids},
    )
    return assert_201(r)


def list_profiles(client, account_id):
    """List all profiles for an account."""
    r = client.get("/api/v1/profiles", params={"account_id": account_id})
    return assert_200(r)


def update_profile(client, profile_id, **kwargs):
    """Partially update a profile. Returns 200."""
    r = client.put(f"/api/v1/profiles/{profile_id}", json=kwargs)
    return assert_200(r)


def delete_profile(client, profile_id):
    """Delete a profile. Returns 204."""
    r = client.delete(f"/api/v1/profiles/{profile_id}")
    return assert_204(r)


def get_homepage(client, profile_id):
    """Fetch the catalog homepage for a profile."""
    r = client.get("/api/v1/home", params={"profile_id": profile_id})
    return assert_200(r)


def get_title_detail(client, title_id):
    """Fetch title detail."""
    r = client.get(f"/api/v1/titles/{title_id}")
    return assert_200(r)


def send_heartbeat(client, profile_id, title_id, position_seconds):
    """Send a playback heartbeat. Returns 200."""
    r = client.post(
        "/api/v1/playback/heartbeat",
        json={
            "profile_id": profile_id,
            "title_id": title_id,
            "position_seconds": position_seconds,
        },
    )
    return assert_200(r)


def get_manifest(client, title_id):
    """Fetch a DASH manifest for a title. Returns 200 with XML text."""
    r = client.get(f"/api/v1/titles/{title_id}/manifest")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    return r.text


def get_segment_bytes(client, segment_id):
    """Fetch raw segment bytes. Returns 200 with bytes."""
    r = client.get(f"/api/v1/segments/{segment_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:200]}"
    return r.content


def search_content(client, query, limit=20):
    """Full-text search. Returns 200."""
    r = client.get("/api/v1/search", params={"q": query, "limit": limit})
    return assert_200(r)


def healthz(client):
    """Hit the health check."""
    r = client.get("/healthz")
    return assert_200(r)
