"""FR3: Stream video segments with ABR quality adaptation.

GET /api/v1/titles/{title_id}/manifest → 200 XML manifest
GET /api/v1/segments/{segment_id} → 200 video/mp2t bytes
Unknown title manifest → 404
Unknown segment → 404
"""

import xml.etree.ElementTree as ET

from verify.acceptance.conftest import (
    assert_404,
    create_account,
    create_profile,
    get_homepage,
    get_manifest,
    get_segment_bytes,
)


def test_manifest_is_valid_xml(client):
    """Manifest endpoint returns well-formed XML with AdaptationSets."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Streamer")

    # Get a title from the homepage.
    homepage = get_homepage(client, profile["profile_id"])
    trending = homepage["trending"]
    assert len(trending) > 0, "Need at least one title in seed data"
    title = trending[0]

    manifest_xml = get_manifest(client, title["title_id"])

    # Parse XML — will raise if malformed.
    root = ET.fromstring(manifest_xml)

    # MPEG-DASH namespace: urn:mpeg:dash:schema:mpd:2011
    # Find AdaptationSets (may be namespaced or not depending on implementation).
    adaptation_sets = root.findall(".//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet")
    if not adaptation_sets:
        adaptation_sets = root.findall(".//AdaptationSet")

    assert len(adaptation_sets) > 0, "Manifest must contain at least one AdaptationSet"

    # Each AdaptationSet should have a SegmentTemplate or SegmentList
    # pointing to segment URLs.
    for as_el in adaptation_sets:
        # Check for SegmentTemplate
        templates = as_el.findall(".//{urn:mpeg:dash:schema:mpd:2011}SegmentTemplate")
        if not templates:
            templates = as_el.findall(".//SegmentTemplate")
        # Check for SegmentList / SegmentTimeline
        timelines = as_el.findall(".//{urn:mpeg:dash:schema:mpd:2011}SegmentTimeline")
        if not timelines:
            timelines = as_el.findall(".//SegmentTimeline")
        # At least one of these should exist.
        assert templates or timelines, "Each AdaptationSet needs SegmentTemplate or SegmentTimeline"


def test_manifest_content_type(client):
    """Manifest returns XML content type."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="CT")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    r = client.get(f"/api/v1/titles/{title['title_id']}/manifest")
    assert r.status_code == 200
    content_type = r.headers.get("content-type", "")
    assert (
        "xml" in content_type.lower() or "dash" in content_type.lower()
    ), f"Expected XML/DASH content-type, got: {content_type}"


def test_manifest_unknown_title(client):
    """Requesting manifest for a non-existent title returns 404."""
    r = client.get("/api/v1/titles/00000000-0000-0000-0000-000000000000/manifest")
    assert_404(r)


def test_segment_returns_bytes(client):
    """Segment endpoint returns raw bytes with video/mp2t Content-Type."""
    account = create_account(client)
    profile = create_profile(client, account["account_id"], name="Bytes")

    homepage = get_homepage(client, profile["profile_id"])
    title = homepage["trending"][0]

    # Get manifest and extract a segment URL from it.
    manifest_xml = get_manifest(client, title["title_id"])
    ET.fromstring(manifest_xml)

    # Look for SegmentTemplate with media attribute containing {segment_id}
    # or direct segment URLs. Simpler: query video_segments for this title
    # via a known endpoint? No — we're black-box. Extract from manifest.
    # Strategy: find a segment URL pattern and construct a valid segment id.
    import re

    # Look for references to /api/v1/segments/ in the manifest.
    segment_urls = re.findall(r"/api/v1/segments/([a-f0-9-]+)", manifest_xml)
    if segment_urls:
        segment_id = segment_urls[0]
        content = get_segment_bytes(client, segment_id)
        assert len(content) > 0, "Segment must return non-empty bytes"


def test_segment_unknown(client):
    """Requesting unknown segment returns 404."""
    r = client.get("/api/v1/segments/00000000-0000-0000-0000-000000000000")
    assert_404(r)
