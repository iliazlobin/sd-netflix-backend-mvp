"""FR5: Create and manage multiple user profiles per account.

POST /api/v1/profiles → 201 create
GET /api/v1/profiles?account_id= → 200 list
PUT /api/v1/profiles/{id} → 200 update
DELETE /api/v1/profiles/{id} → 204 delete
Duplicate name within account → 409
Unknown account → 404
Empty name → 422
"""

from verify.acceptance.conftest import (
    assert_404,
    assert_409,
    assert_422,
    create_account,
    create_profile,
    delete_profile,
    list_profiles,
    update_profile,
)


def test_create_profile_201(client):
    """Creating a valid profile returns 201 with profile data."""
    account = create_account(client)
    body = create_profile(client, account["account_id"], name="Main Profile")

    assert body["name"] == "Main Profile"
    assert body["account_id"] == account["account_id"]
    assert "profile_id" in body
    assert body["is_kids"] is False


def test_create_profile_with_is_kids(client):
    """is_kids flag is stored and returned."""
    account = create_account(client)
    body = create_profile(client, account["account_id"], name="Kids Corner", is_kids=True)

    assert body["is_kids"] is True


def test_list_profiles(client):
    """Listing profiles returns all profiles for an account."""
    account = create_account(client)
    p1 = create_profile(client, account["account_id"], name="Profile A")
    p2 = create_profile(client, account["account_id"], name="Profile B")

    result = list_profiles(client, account["account_id"])
    profiles = result["profiles"]

    assert len(profiles) == 2
    profile_ids = {p["profile_id"] for p in profiles}
    assert p1["profile_id"] in profile_ids
    assert p2["profile_id"] in profile_ids


def test_duplicate_name_409(client):
    """Creating a profile with an existing name in the same account returns 409."""
    account = create_account(client)
    create_profile(client, account["account_id"], name="Duplicate")

    # Second profile with same name.
    r = client.post(
        "/api/v1/profiles",
        json={"account_id": account["account_id"], "name": "Duplicate"},
    )
    assert_409(r)


def test_update_profile_name(client):
    """Updating a profile name works and returns 200."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Old Name")

    updated = update_profile(client, profile["profile_id"], name="New Name")
    assert updated["name"] == "New Name"


def test_update_duplicate_name_409(client):
    """Updating to a name already used in the account returns 409."""
    account = create_account(client)
    create_profile(client, account["account_id"], name="Existing")
    p2 = create_profile(client, account["account_id"], name="Other")

    r = client.put(f"/api/v1/profiles/{p2['profile_id']}", json={"name": "Existing"})
    assert_409(r)


def test_delete_profile_204(client):
    """Deleting a profile returns 204 and removes it from listing."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="To Delete")

    delete_profile(client, profile["profile_id"])

    # Profile no longer in list.
    result = list_profiles(client, account["account_id"])
    profile_ids = {p["profile_id"] for p in result["profiles"]}
    assert profile["profile_id"] not in profile_ids


def test_update_unknown_profile_404(client):
    """Updating a non-existent profile returns 404."""
    r = client.put(
        "/api/v1/profiles/00000000-0000-0000-0000-000000000000",
        json={"name": "Ghost"},
    )
    assert_404(r)


def test_delete_unknown_profile_404(client):
    """Deleting a non-existent profile returns 404."""
    r = client.delete("/api/v1/profiles/00000000-0000-0000-0000-000000000000")
    assert_404(r)


def test_create_profile_empty_name_422(client):
    """Creating a profile with an empty name returns 422."""
    account = create_account(client)
    r = client.post(
        "/api/v1/profiles",
        json={"account_id": account["account_id"], "name": ""},
    )
    assert_422(r)


def test_create_profile_unknown_account_404(client):
    """Creating a profile for a non-existent account returns 404."""
    r = client.post(
        "/api/v1/profiles",
        json={
            "account_id": "00000000-0000-0000-0000-000000000000",
            "name": "Orphan",
        },
    )
    assert_404(r)
