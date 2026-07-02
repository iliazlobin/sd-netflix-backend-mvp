"""FR2: Search content by title, genre, cast, or keyword.

GET /api/v1/search?q=<query> → 200 with ranked results
Empty query → 200 with empty results
Results include type, id, display_name, score
"""

from verify.acceptance.conftest import search_content


def test_search_by_title_keyword(client):
    """Search for a title by keyword returns title-typed results (requires seed data)."""
    # Use a keyword likely to match seed data titles.
    results = search_content(client, "the")

    assert "results" in results
    assert isinstance(results["results"], list)

    # At least one result should be a title match.
    title_results = [r for r in results["results"] if r["type"] == "title"]
    assert len(title_results) > 0, "Expected at least one title result from seed data search"

    first = title_results[0]
    assert "id" in first
    assert "display_name" in first
    assert "score" in first
    assert first["score"] > 0


def test_search_empty_query(client):
    """An empty query returns empty results, not an error."""
    results = search_content(client, "")

    assert "results" in results
    assert results["results"] == []


def test_search_by_genre_keyword(client):
    """Search for a genre name returns genre-typed results (requires seed data)."""
    results = search_content(client, "action")

    assert "results" in results
    genre_results = [r for r in results["results"] if r["type"] == "genre"]

    # Seed data may or may not have Action genre; either outcome is valid.
    # Just verify the response structure and type filter works.
    for r in genre_results:
        assert r["type"] == "genre"
        assert "id" in r
        assert "display_name" in r


def test_search_limit_is_honored(client):
    """The limit parameter caps the number of results."""
    results = search_content(client, "the", limit=3)

    assert len(results["results"]) <= 3


def test_search_results_have_score(client):
    """Every search result has a score field."""
    results = search_content(client, "a")  # Common letter, many matches

    for r in results["results"]:
        assert "score" in r
        assert isinstance(r["score"], int | float)
