"""StreamingService — DASH manifest generation and mock segment serving."""

from __future__ import annotations

import os
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.config import settings
from netflix.models import VideoSegment


class StreamingService:
    """Business logic for ABR streaming — manifest XML and segment bytes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_manifest(self, title_id: uuid.UUID) -> str | None:
        """Generate an MPEG-DASH .mpd manifest for a title."""
        stmt = (
            select(VideoSegment)
            .where(VideoSegment.title_id == title_id)
            .order_by(VideoSegment.quality, VideoSegment.segment_index)
        )
        result = await self._session.execute(stmt)
        segments = result.scalars().all()

        if not segments:
            return None

        # Build MPD XML
        mpd = Element(
            "MPD",
            xmlns="urn:mpeg:dash:schema:mpd:2011",
            profiles="urn:mpeg:dash:profile:isoff-live:2011",
            type="static",
            minBufferTime="PT2S",
        )
        period = SubElement(mpd, "Period")

        # Group segments by quality
        quality_groups: dict[str, list[VideoSegment]] = {}
        for seg in segments:
            quality_groups.setdefault(seg.quality, []).append(seg)

        for quality, segs in quality_groups.items():
            bandwidth = {
                "1080p": "5000000",
                "720p": "2500000",
                "480p": "1000000",
                "240p": "500000",
            }.get(quality, "1000000")

            adapter = SubElement(
                period,
                "AdaptationSet",
                mimeType="video/mp2t",
                contentType="video",
                bandwidth=bandwidth,
            )
            rep = SubElement(
                adapter,
                "Representation",
                id=quality,
                bandwidth=bandwidth,
            )
            seg_timeline = SubElement(rep, "SegmentTimeline")

            for seg in segs:
                s = SubElement(seg_timeline, "S")
                s.set("t", str(seg.segment_index * seg.duration_seconds))
                s.set("d", str(seg.duration_seconds))
                s.set("r", "0")
                # Link to segment endpoint
                seg_url = SubElement(rep, "SegmentURL")
                seg_url.set(
                    "media",
                    f"/api/v1/segments/{seg.segment_id}",
                )

        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
        return xml_declaration + tostring(mpd, encoding="unicode")

    async def get_segment(self, segment_id: uuid.UUID) -> tuple[bytes, str] | None:
        """Look up a segment and read its bytes from disk.

        Returns (bytes, content_type) or None if not found.
        """
        stmt = select(VideoSegment).where(VideoSegment.segment_id == segment_id)
        result = await self._session.execute(stmt)
        segment = result.scalar_one_or_none()
        if segment is None:
            return None

        file_path = segment.file_path
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.mock_segments_dir, file_path)

        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            return None

        return data, "video/mp2t"
