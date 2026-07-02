"""FR4: Resume playback from last position via heartbeat.

POST /api/v1/playback/heartbeat → 200 upserts position
Subsequent homepage load shows continue-watching with updated position
Unknown profile → 404
Unknown title → 404
Negative position → 422
"""

from verify.acceptance.conftest import (
    assert_404,
    assert_422,
    create_account,
    create_profile,
    get_homepage,
    send_heartbeat,
)


def test_heartbeat_200(client):
    """A valid heartbeat returns 200 with current position."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Watcher")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    body = send_heartbeat(client, profile["profile_id"], title["title_id"], 300)
    assert body["profile_id"] == profile["profile_id"]
    assert body["title_id"] == title["title_id"]
    assert body["position_seconds"] == 300


def test_heartbeat_updates_position(client):
    """Subsequent heartbeat updates position_seconds."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Updater")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    # First heartbeat.
    body1 = send_heartbeat(client, profile["profile_id"], title["title_id"], 60)
    assert body1["position_seconds"] == 60

    # Second heartbeat further in.
    body2 = send_heartbeat(client, profile["profile_id"], title["title_id"], 600)
    assert body2["position_seconds"] == 600


def test_heartbeat_unknown_profile(client):
    """Heartbeat for unknown profile returns 404."""
    r = client.post(
        "/api/v1/playback/heartbeat",
        json={
            "profile_id": "00000000-0000-0000-0000-000000000000",
            "title_id": "00000000-0000-0000-0000-000000000000",
            "position_seconds": 0,
        },
    )
    assert_404(r)


def test_heartbeat_unknown_title(client):
    """Heartbeat for unknown title returns 404."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="404Test")

    r = client.post(
        "/api/v1/playback/heartbeat",
        json={
            "profile_id": profile["profile_id"],
            "title_id": "00000000-0000-0000-0000-000000000000",
            "position_seconds": 0,
        },
    )
    assert_404(r)


def test_heartbeat_negative_position(client):
    """Negative position_seconds returns 422."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Neg")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    r = client.post(
        "/api/v1/playback/heartbeat",
        json={
            "profile_id": profile["profile_id"],
            "title_id": title["title_id"],
            "position_seconds": -1,
        },
    )
    assert_422(r)


def test_position_persists_across_requests(client):
    """Position from heartbeat is reflected in continue-watching on homepage."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Persist")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    # Watch 45 seconds.
    send_heartbeat(client, profile["profile_id"], title["title_id"], 45)

    # Reload homepage — should see position.
    homepage2 = get_homepage(client, profile["profile_id"])
    cw = homepage2["continue_watching"]

    watched = next((item for item in cw if item["title_id"] == title["title_id"]), None)
    assert watched is not None, "Expected title in continue-watching after heartbeat"
    assert watched["position_seconds"] >= 45
