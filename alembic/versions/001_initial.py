"""Initial migration — create all 10 tables with constraints and indexes.

Tables: accounts, profiles, titles, genres, title_genres, cast_members,
        title_cast, playback_progress, watch_history, video_segments
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- accounts ---
    op.create_table(
        "accounts",
        sa.Column(
            "account_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("account_id"),
        sa.UniqueConstraint("email", name="uq_accounts_email"),
    )

    # --- profiles ---
    op.create_table(
        "profiles",
        sa.Column(
            "profile_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_kids", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"]),
        sa.UniqueConstraint("account_id", "name", name="uq_profile_name_per_account"),
    )

    # --- titles ---
    op.create_table(
        "titles",
        sa.Column(
            "title_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("synopsis", sa.Text(), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=False),
        sa.Column("maturity_rating", sa.String(10), nullable=False),
        sa.Column("poster_url", sa.String(500), nullable=False),
        sa.Column("backdrop_url", sa.String(500), nullable=False),
        sa.Column("title_type", sa.String(20), nullable=False),
        sa.Column("trending_score", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "fts_vector",
            TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(synopsis, ''))",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("title_id"),
        sa.CheckConstraint("release_year >= 1888", name="ck_titles_release_year"),
    )
    op.create_index("ix_titles_fts_vector", "titles", ["fts_vector"], postgresql_using="gin")
    op.create_index("ix_titles_trending_score", "titles", ["trending_score"])

    # --- genres ---
    op.create_table(
        "genres",
        sa.Column(
            "genre_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "fts_vector",
            TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', coalesce(name, ''))",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("genre_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_genres_fts_vector", "genres", ["fts_vector"], postgresql_using="gin")

    # --- title_genres ---
    op.create_table(
        "title_genres",
        sa.Column("title_id", sa.UUID(), nullable=False),
        sa.Column("genre_id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("title_id", "genre_id"),
        sa.ForeignKeyConstraint(["title_id"], ["titles.title_id"]),
        sa.ForeignKeyConstraint(["genre_id"], ["genres.genre_id"]),
        sa.UniqueConstraint("title_id", "genre_id", name="uq_title_genre"),
    )

    # --- cast_members ---
    op.create_table(
        "cast_members",
        sa.Column(
            "cast_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "fts_vector",
            TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', coalesce(name, ''))",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("cast_id"),
    )
    op.create_index(
        "ix_cast_members_fts_vector", "cast_members", ["fts_vector"], postgresql_using="gin"
    )

    # --- title_cast ---
    op.create_table(
        "title_cast",
        sa.Column("title_id", sa.UUID(), nullable=False),
        sa.Column("cast_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("title_id", "cast_id"),
        sa.ForeignKeyConstraint(["title_id"], ["titles.title_id"]),
        sa.ForeignKeyConstraint(["cast_id"], ["cast_members.cast_id"]),
        sa.UniqueConstraint("title_id", "cast_id", "role", name="uq_title_cast_role"),
    )

    # --- playback_progress ---
    op.create_table(
        "playback_progress",
        sa.Column(
            "progress_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("profile_id", sa.UUID(), nullable=False),
        sa.Column("title_id", sa.UUID(), nullable=False),
        sa.Column("position_seconds", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("progress_id"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.profile_id"]),
        sa.ForeignKeyConstraint(["title_id"], ["titles.title_id"]),
        sa.UniqueConstraint("profile_id", "title_id", name="uq_progress_profile_title"),
    )

    # --- watch_history ---
    op.create_table(
        "watch_history",
        sa.Column(
            "history_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("profile_id", sa.UUID(), nullable=False),
        sa.Column("title_id", sa.UUID(), nullable=False),
        sa.Column(
            "watched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("history_id"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.profile_id"]),
        sa.ForeignKeyConstraint(["title_id"], ["titles.title_id"]),
    )

    # --- video_segments ---
    op.create_table(
        "video_segments",
        sa.Column(
            "segment_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("title_id", sa.UUID(), nullable=False),
        sa.Column("quality", sa.String(10), nullable=False),
        sa.Column("segment_index", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("segment_id"),
        sa.ForeignKeyConstraint(["title_id"], ["titles.title_id"]),
        sa.UniqueConstraint(
            "title_id",
            "quality",
            "segment_index",
            name="uq_segment_title_quality_index",
        ),
    )


def downgrade() -> None:
    op.drop_table("video_segments")
    op.drop_table("watch_history")
    op.drop_table("playback_progress")
    op.drop_table("title_cast")
    op.drop_table("cast_members")
    op.drop_table("title_genres")
    op.drop_table("genres")
    op.drop_table("titles")
    op.drop_table("profiles")
    op.drop_table("accounts")
