"""Seed data migration — create demo content for acceptance testing.

Creates:
- 1 account with 3 profiles
- ~30 titles across 6 genres with cast members
- Video segment rows per title (4 quality levels, 5 segments each)
- Mock .ts files for segments
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "002_seed"
down_revision = "001_initial"
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Helper: generate deterministic UUIDs for seed data
# ---------------------------------------------------------------------------


def _ns_uuid(ns: str, name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"netflix-seed/{ns}/{name}"))


GENRES = [
    ("action", "Action"),
    ("comedy", "Comedy"),
    ("drama", "Drama"),
    ("scifi", "Sci-Fi"),
    ("thriller", "Thriller"),
    ("documentary", "Documentary"),
]

TITLES_DATA = [
    # (slug, title, synopsis, year, rating, type, score, genre_slugs)
    (
        "die-hard",
        "Die Hard",
        "A New York cop battles terrorists in an LA skyscraper.",
        1988,
        "R",
        "movie",
        9.2,
        ["action"],
    ),
    (
        "mad-max",
        "Mad Max: Fury Road",
        "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler.",
        2015,
        "R",
        "movie",
        9.0,
        ["action"],
    ),
    (
        "john-wick",
        "John Wick",
        "A retired hitman seeks vengeance after a tragic loss.",
        2014,
        "R",
        "movie",
        8.8,
        ["action"],
    ),
    (
        "dark-knight",
        "The Dark Knight",
        "Batman faces the Joker in a battle for Gotham's soul.",
        2008,
        "PG-13",
        "movie",
        9.5,
        ["action", "thriller"],
    ),
    (
        "gladiator",
        "Gladiator",
        "A Roman general seeks vengeance as a gladiator.",
        2000,
        "R",
        "movie",
        8.5,
        ["action", "drama"],
    ),
    (
        "hangover",
        "The Hangover",
        "Three friends search for their missing friend after a wild bachelor party.",
        2009,
        "R",
        "movie",
        7.5,
        ["comedy"],
    ),
    (
        "superbad",
        "Superbad",
        "Two high school friends try to make the most of their last party.",
        2007,
        "R",
        "movie",
        7.8,
        ["comedy"],
    ),
    (
        "bridesmaids",
        "Bridesmaids",
        "A maid of honor's life unravels as she plans her best friend's wedding.",
        2011,
        "R",
        "movie",
        7.2,
        ["comedy"],
    ),
    (
        "office-s1",
        "The Office (US)",
        "A mockumentary about the employees of Dunder Mifflin.",
        2005,
        "PG",
        "series",
        8.9,
        ["comedy"],
    ),
    (
        "parks-rec",
        "Parks and Recreation",
        "A bureaucrat tries to turn a pit into a park.",
        2009,
        "PG-13",
        "series",
        8.6,
        ["comedy"],
    ),
    (
        "shawshank",
        "The Shawshank Redemption",
        "A banker is sentenced to life in Shawshank prison.",
        1994,
        "R",
        "movie",
        9.3,
        ["drama"],
    ),
    (
        "godfather",
        "The Godfather",
        "The aging patriarch of an organized crime dynasty transfers control to his son.",
        1972,
        "R",
        "movie",
        9.2,
        ["drama", "thriller"],
    ),
    (
        "schindlers",
        "Schindler's List",
        "A businessman saves Jewish refugees during the Holocaust.",
        1993,
        "R",
        "movie",
        9.0,
        ["drama"],
    ),
    (
        "breaking-bad",
        "Breaking Bad",
        "A chemistry teacher turned meth maker navigates the criminal underworld.",
        2008,
        "R",
        "series",
        9.5,
        ["drama", "thriller"],
    ),
    (
        "succession",
        "Succession",
        "A family struggles for control of a global media empire.",
        2018,
        "R",
        "series",
        8.9,
        ["drama"],
    ),
    (
        "inception",
        "Inception",
        "A thief who steals corporate secrets through dream-sharing technology.",
        2010,
        "PG-13",
        "movie",
        8.8,
        ["scifi", "thriller"],
    ),
    (
        "matrix",
        "The Matrix",
        "A computer hacker learns the truth about reality.",
        1999,
        "R",
        "movie",
        8.7,
        ["scifi", "action"],
    ),
    (
        "blade-runner",
        "Blade Runner 2049",
        "A new blade runner unearths a long-buried secret.",
        2017,
        "R",
        "movie",
        8.0,
        ["scifi", "thriller"],
    ),
    (
        "dune",
        "Dune",
        "A noble family becomes embroiled in a war for control of the galaxy's most valuable asset.",
        2021,
        "PG-13",
        "movie",
        8.5,
        ["scifi"],
    ),
    (
        "stranger-things",
        "Stranger Things",
        "A group of kids uncover supernatural mysteries in their small town.",
        2016,
        "PG-13",
        "series",
        8.7,
        ["scifi", "thriller"],
    ),
    (
        "silence-lambs",
        "The Silence of the Lambs",
        "An FBI trainee seeks help from a cannibalistic serial killer.",
        1991,
        "R",
        "movie",
        8.6,
        ["thriller"],
    ),
    (
        "gone-girl",
        "Gone Girl",
        "A husband becomes the prime suspect in his wife's disappearance.",
        2014,
        "R",
        "movie",
        8.1,
        ["thriller", "drama"],
    ),
    (
        "parasite",
        "Parasite",
        "A poor family schemes their way into a wealthy household.",
        2019,
        "R",
        "movie",
        9.0,
        ["thriller", "drama"],
    ),
    (
        "se7en",
        "Se7en",
        "Two detectives hunt a serial killer who uses the seven deadly sins.",
        1995,
        "R",
        "movie",
        8.6,
        ["thriller"],
    ),
    (
        "planet-earth",
        "Planet Earth",
        "A documentary series exploring the diversity of life on Earth.",
        2006,
        "G",
        "series",
        9.4,
        ["documentary"],
    ),
    (
        "our-planet",
        "Our Planet",
        "A documentary series showcasing Earth's natural habitats.",
        2019,
        "G",
        "series",
        9.3,
        ["documentary"],
    ),
    (
        "blue-planet",
        "Blue Planet II",
        "A documentary series exploring the world's oceans.",
        2017,
        "G",
        "series",
        9.2,
        ["documentary"],
    ),
    (
        "free-solo",
        "Free Solo",
        "A rock climber attempts to scale El Capitan without ropes.",
        2018,
        "PG-13",
        "movie",
        8.3,
        ["documentary"],
    ),
    (
        "march-penguins",
        "March of the Penguins",
        "The annual journey of Emperor penguins across Antarctica.",
        2005,
        "G",
        "movie",
        7.6,
        ["documentary"],
    ),
    (
        "chernobyl",
        "Chernobyl",
        "A dramatization of the 1986 Chernobyl nuclear disaster.",
        2019,
        "R",
        "series",
        9.4,
        ["drama", "thriller"],
    ),
]

CAST_MEMBERS = [
    ("bruce-willis", "Bruce Willis"),
    ("charlize-theron", "Charlize Theron"),
    ("keanu-reeves", "Keanu Reeves"),
    ("christian-bale", "Christian Bale"),
    ("heath-ledger", "Heath Ledger"),
    ("russell-crowe", "Russell Crowe"),
    ("bradley-cooper", "Bradley Cooper"),
    ("jonah-hill", "Jonah Hill"),
    ("kristen-wiig", "Kristen Wiig"),
    ("steve-carell", "Steve Carell"),
    ("amy-poehler", "Amy Poehler"),
    ("tim-robbins", "Tim Robbins"),
    ("marlon-brando", "Marlon Brando"),
    ("liam-neeson", "Liam Neeson"),
    ("brian-cranston", "Brian Cranston"),
    ("jeremy-strong", "Jeremy Strong"),
    ("leonardo-dicaprio", "Leonardo DiCaprio"),
    ("keanu-reeves2", "Keanu Reeves"),
    ("ryan-gosling", "Ryan Gosling"),
    ("timothee-chalamet", "Timothée Chalamet"),
    ("millie-bobby-brown", "Millie Bobby Brown"),
    ("jodie-foster", "Jodie Foster"),
    ("anthony-hopkins", "Anthony Hopkins"),
    ("ben-affleck", "Ben Affleck"),
    ("rosamund-pike", "Rosamund Pike"),
    ("song-kang-ho", "Song Kang-ho"),
    ("morgan-freeman", "Morgan Freeman"),
    ("david-attenborough", "David Attenborough"),
    ("alex-honnold", "Alex Honnold"),
    ("jared-harris", "Jared Harris"),
    ("stacy-keach", "Stacy Keach"),
    ("gary-oldman", "Gary Oldman"),
    ("halle-berry", "Halle Berry"),
    ("zendaya", "Zendaya"),
    ("oscar-isaac", "Oscar Isaac"),
    ("rebecca-ferguson", "Rebecca Ferguson"),
    ("winona-ryder", "Winona Ryder"),
    ("david-harbour", "David Harbour"),
]

TITLE_CAST = [
    # (title_slug, cast_slug, role)
    ("die-hard", "bruce-willis", "John McClane"),
    ("mad-max", "charlize-theron", "Furiosa"),
    ("john-wick", "keanu-reeves", "John Wick"),
    ("dark-knight", "christian-bale", "Bruce Wayne / Batman"),
    ("dark-knight", "heath-ledger", "The Joker"),
    ("gladiator", "russell-crowe", "Maximus Decimus Meridius"),
    ("hangover", "bradley-cooper", "Phil Wenneck"),
    ("hangover", "stacy-keach", "Stu Price"),
    ("superbad", "jonah-hill", "Seth"),
    ("bridesmaids", "kristen-wiig", "Annie Walker"),
    ("office-s1", "steve-carell", "Michael Scott"),
    ("parks-rec", "amy-poehler", "Leslie Knope"),
    ("shawshank", "tim-robbins", "Andy Dufresne"),
    ("godfather", "marlon-brando", "Don Vito Corleone"),
    ("schindlers", "liam-neeson", "Oskar Schindler"),
    ("breaking-bad", "brian-cranston", "Walter White"),
    ("succession", "jeremy-strong", "Kendall Roy"),
    ("inception", "leonardo-dicaprio", "Dom Cobb"),
    ("matrix", "keanu-reeves", "Neo"),
    ("blade-runner", "ryan-gosling", "Officer K"),
    ("dune", "timothee-chalamet", "Paul Atreides"),
    ("dune", "zendaya", "Chani"),
    ("dune", "oscar-isaac", "Duke Leto Atreides"),
    ("dune", "rebecca-ferguson", "Lady Jessica"),
    ("stranger-things", "millie-bobby-brown", "Eleven"),
    ("stranger-things", "winona-ryder", "Joyce Byers"),
    ("stranger-things", "david-harbour", "Jim Hopper"),
    ("silence-lambs", "jodie-foster", "Clarice Starling"),
    ("silence-lambs", "anthony-hopkins", "Hannibal Lecter"),
    ("gone-girl", "ben-affleck", "Nick Dunne"),
    ("gone-girl", "rosamund-pike", "Amy Dunne"),
    ("parasite", "song-kang-ho", "Kim Ki-taek"),
    ("se7en", "morgan-freeman", "Somerset"),
    ("planet-earth", "david-attenborough", "Narrator"),
    ("our-planet", "david-attenborough", "Narrator"),
    ("blue-planet", "david-attenborough", "Narrator"),
    ("free-solo", "alex-honnold", "Alex Honnold (self)"),
    ("chernobyl", "jared-harris", "Valery Legasov"),
    ("chernobyl", "gary-oldman", "Grigori Medvedev"),
    ("matrix", "keanu-reeves", "Neo"),
    ("matrix", "gary-oldman", "Cypher"),
    ("matrix", "halle-berry", "Zee"),
    ("inception", "leonardo-dicaprio", "Dom Cobb"),
]

# Quality levels for video segments
QUALITIES = ["1080p", "720p", "480p", "240p"]
SEGMENTS_PER_TITLE = 5
MOCK_FILE_PATHS = {
    "1080p": "/app/data/segments/mock_1080p.ts",
    "720p": "/app/data/segments/mock_720p.ts",
    "480p": "/app/data/segments/mock_480p.ts",
    "240p": "/app/data/segments/mock_240p.ts",
}
SEGMENT_SIZE_BYTES = {
    "1080p": 4096,
    "720p": 3072,
    "480p": 2048,
    "240p": 1024,
}
SEGMENT_DURATION = 4  # seconds


def upgrade() -> None:
    conn = op.get_bind()

    # --- Create account ---
    account_id = _ns_uuid("account", "main")
    conn.execute(
        sa.text("""
            INSERT INTO accounts (account_id, email, created_at)
            VALUES (:id, :email, :created_at)
            ON CONFLICT (account_id) DO NOTHING
        """),
        {
            "id": account_id,
            "email": "user@netflix-mvp.com",
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        },
    )

    # --- Create profiles ---
    profiles = [
        ("profile-adult", account_id, "Ilia", False),
        ("profile-kids", account_id, "Kids", True),
        ("profile-guest", account_id, "Guest", False),
    ]
    for slug, aid, name, kids in profiles:
        conn.execute(
            sa.text("""
                INSERT INTO profiles (profile_id, account_id, name, is_kids, created_at)
                VALUES (:id, :aid, :name, :kids, :created_at)
                ON CONFLICT (profile_id) DO NOTHING
            """),
            {
                "id": _ns_uuid("profile", slug),
                "aid": aid,
                "name": name,
                "kids": kids,
                "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            },
        )

    # --- Create genres ---
    for slug, name in GENRES:
        conn.execute(
            sa.text("""
                INSERT INTO genres (genre_id, name)
                VALUES (:id, :name)
                ON CONFLICT (genre_id) DO NOTHING
            """),
            {"id": _ns_uuid("genre", slug), "name": name},
        )

    # --- Create titles ---
    for slug, title, synopsis, year, rating, ttype, score, _ in TITLES_DATA:
        conn.execute(
            sa.text("""
                INSERT INTO titles (title_id, title, synopsis, release_year,
                                    maturity_rating, poster_url, backdrop_url,
                                    title_type, trending_score, created_at)
                VALUES (:id, :title, :synopsis, :year, :rating,
                        :poster, :backdrop, :ttype, :score, :created_at)
                ON CONFLICT (title_id) DO NOTHING
            """),
            {
                "id": _ns_uuid("title", slug),
                "title": title,
                "synopsis": synopsis,
                "year": year,
                "rating": rating,
                "poster": f"https://picsum.photos/seed/{slug}/300/450",
                "backdrop": f"https://picsum.photos/seed/{slug}-bg/1280/720",
                "ttype": ttype,
                "score": score,
                "created_at": datetime(year, 6, 1, tzinfo=UTC),
            },
        )

    # --- Create title-genre associations ---
    for slug, _, _, _, _, _, _, genre_slugs in TITLES_DATA:
        for genre_slug in genre_slugs:
            conn.execute(
                sa.text("""
                    INSERT INTO title_genres (title_id, genre_id)
                    VALUES (:title_id, :genre_id)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title_id": _ns_uuid("title", slug),
                    "genre_id": _ns_uuid("genre", genre_slug),
                },
            )

    # --- Create cast members ---
    for slug, name in CAST_MEMBERS:
        conn.execute(
            sa.text("""
                INSERT INTO cast_members (cast_id, name)
                VALUES (:id, :name)
                ON CONFLICT (cast_id) DO NOTHING
            """),
            {"id": _ns_uuid("cast", slug), "name": name},
        )

    # --- Create title-cast associations ---
    for title_slug, cast_slug, role in TITLE_CAST:
        conn.execute(
            sa.text("""
                INSERT INTO title_cast (title_id, cast_id, role)
                VALUES (:title_id, :cast_id, :role)
                ON CONFLICT DO NOTHING
            """),
            {
                "title_id": _ns_uuid("title", title_slug),
                "cast_id": _ns_uuid("cast", cast_slug),
                "role": role,
            },
        )

    # --- Create video segments ---
    for slug, _, _, _, _, _, _, _ in TITLES_DATA:
        title_id = _ns_uuid("title", slug)
        for quality in QUALITIES:
            for idx in range(SEGMENTS_PER_TITLE):
                seg_id = _ns_uuid("segment", f"{slug}/{quality}/{idx}")
                conn.execute(
                    sa.text("""
                        INSERT INTO video_segments
                            (segment_id, title_id, quality, segment_index,
                             file_path, duration_seconds, size_bytes)
                        VALUES (:id, :title_id, :quality, :idx,
                                :file_path, :duration, :size)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "id": seg_id,
                        "title_id": title_id,
                        "quality": quality,
                        "idx": idx,
                        "file_path": MOCK_FILE_PATHS[quality],
                        "duration": SEGMENT_DURATION,
                        "size": SEGMENT_SIZE_BYTES[quality],
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM video_segments"))
    conn.execute(sa.text("DELETE FROM title_cast"))
    conn.execute(sa.text("DELETE FROM cast_members"))
    conn.execute(sa.text("DELETE FROM title_genres"))
    conn.execute(sa.text("DELETE FROM watch_history"))
    conn.execute(sa.text("DELETE FROM playback_progress"))
    conn.execute(sa.text("DELETE FROM titles"))
    conn.execute(sa.text("DELETE FROM genres"))
    conn.execute(sa.text("DELETE FROM profiles"))
    conn.execute(sa.text("DELETE FROM accounts"))
