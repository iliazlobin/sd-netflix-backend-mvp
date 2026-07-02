"""FR1: Browse a personalized homepage with row-based title listings.

GET /api/v1/home?profile_id=<uuid> → 200 with continue_watching, trending, genre_rows
Unknown profile → 404
Continue-watching shows recently watched titles with positions
"""

from verify.acceptance.conftest import (
    assert_404,
    create_account,
    create_profile,
    get_homepage,
    send_heartbeat,
)


def test_homepage_structure(client):
    """Homepage returns three expected row sections."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Alice")

    homepage = get_homepage(client, profile["profile_id"])

    assert "continue_watching" in homepage
    assert "trending" in homepage
    assert "genre_rows" in homepage
    assert isinstance(homepage["continue_watching"], list)
    assert isinstance(homepage["trending"], list)
    assert isinstance(homepage["genre_rows"], list)


def test_homepage_unknown_profile(client):
    """Requesting homepage for a non-existent profile returns 404."""
    r = client.get(
        "/api/v1/home",
        params={"profile_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert_404(r)


def test_trending_has_items(client):
    """Trending row contains titles with expected fields (requires seed data)."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Bob")

    homepage = get_homepage(client, profile["profile_id"])
    trending = homepage["trending"]

    # Seed data should provide trending titles.
    assert len(trending) > 0, "Expected at least one trending title from seed data"

    first = trending[0]
    assert "title_id" in first
    assert "title" in first
    assert "poster_url" in first


def test_genre_rows_structure(client):
    """Genre rows are lists of {genre_name, titles} dicts (requires seed data)."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Charlie")

    homepage = get_homepage(client, profile["profile_id"])
    genre_rows = homepage["genre_rows"]

    assert len(genre_rows) > 0, "Expected at least one genre row from seed data"

    first_row = genre_rows[0]
    assert "genre_name" in first_row
    assert "titles" in first_row
    assert isinstance(first_row["titles"], list)
    assert len(first_row["titles"]) > 0


def test_continue_watching_after_heartbeat(client):
    """After sending a heartbeat, continue-watching includes the title with position."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Dana")

    # Find a title to watch — grab one from trending.
    homepage = get_homepage(client, profile["profile_id"])
    trending = homepage["trending"]
    assert len(trending) > 0, "Need at least one title in seed data"
    title = trending[0]

    # Send heartbeat to mark this title as watched.
    send_heartbeat(client, profile["profile_id"], title["title_id"], 120)

    # Reload homepage; continue-watching should include this title.
    homepage2 = get_homepage(client, profile["profile_id"])
    cw = homepage2["continue_watching"]

    watched_ids = {item["title_id"] for item in cw}
    assert title["title_id"] in watched_ids, (
        f"Expected {title['title_id']} in continue-watching after heartbeat"
    )

    # The position should be at least the heartbeat value.
    watched_item = next(item for item in cw if item["title_id"] == title["title_id"])
    assert watched_item["position_seconds"] >= 120
