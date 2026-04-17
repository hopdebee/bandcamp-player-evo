# coding=utf-8
"""Small Python client for Bandcamp Discover."""

from __future__ import annotations

import math
from typing import Iterable, List, Optional
from urllib.parse import urlsplit, urlunsplit

import requests


DISCOVER_URL = "https://bandcamp.com/api/discover/1/discover_web"
REQUEST_TIMEOUT = 20


class NoDiscoverResultsError(RuntimeError):
    """Raised when Bandcamp Discover returns no playable items."""


def _clean_tag(tag: Optional[str]) -> Optional[str]:
    """Normalize user input before sending it to Discover."""
    if tag is None:
        return None
    cleaned = tag.strip()
    return cleaned or None


def _build_tag_norm_names(genre: str, subgenre: Optional[str] = None) -> List[str]:
    """Build the tag list for a Discover request."""
    tags = []
    for tag in (_clean_tag(genre), _clean_tag(subgenre)):
        if tag:
            tags.append(tag)
    return tags


def _build_payload(
    tag_norm_names: Iterable[str], size: int = 1, cursor: str = "*"
) -> dict:
    """Construct a Discover API request payload."""
    return {
        "category_id": 0,
        "cursor": cursor,
        "geoname_id": 0,
        "include_result_types": ["a", "s"],
        "size": size,
        "slice": "rand",
        "tag_norm_names": list(tag_norm_names),
        "time_facet_id": None,
    }


def _format_page_label(tag_norm_names: Iterable[str]) -> str:
    """Format the discover source as a human-readable page label."""
    tags = list(tag_norm_names)
    if not tags:
        return "all"
    return "/".join(tags)


def _normalize_item_url(url: Optional[str]) -> Optional[str]:
    """Remove Bandcamp tracking params and keep only playable item URLs."""
    if not url:
        return None

    parts = urlsplit(url)
    normalized = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    if "/album/" in normalized or "/track/" in normalized:
        return normalized
    return None


def _extract_album_urls(data: dict) -> List[str]:
    """Extract playable Bandcamp item URLs from a Discover response."""
    urls = []
    for item in data.get("results", []):
        url = _normalize_item_url(item.get("item_url"))
        if url:
            urls.append(url)
    return urls


def _parse_discover_batch(data: dict, size: int) -> dict:
    """Parse a discover response into URLs and pagination metadata."""
    urls = _extract_album_urls(data)
    result_count = int(data.get("result_count") or 0)
    page_size = max(size, 1)
    api_page_count = int(math.ceil(float(result_count) / float(page_size))) if result_count else 0
    return {
        "urls": urls,
        "result_count": result_count,
        "api_page_count": api_page_count,
        "cursor": data.get("cursor"),
    }


def _fetch_discover(
    session: requests.Session,
    tag_norm_names: Iterable[str],
    size: int,
    cursor: str = "*",
) -> dict:
    """Execute one Discover request and return playable URLs plus metadata."""
    response = session.post(
        DISCOVER_URL,
        json=_build_payload(tag_norm_names, size=size, cursor=cursor),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return _parse_discover_batch(response.json(), size=size)


def discover_album_urls(
    genre: str, subgenre: Optional[str] = None, size: int = 1
) -> List[str]:
    """Discover Bandcamp album URLs with a deterministic fallback ladder."""
    urls, _metadata = discover_album_urls_with_source(genre, subgenre, size=size)
    return urls


def discover_album_urls_with_source(
    genre: str, subgenre: Optional[str] = None, size: int = 1
) -> tuple[List[str], dict]:
    """Discover Bandcamp album URLs and return source and pagination metadata."""
    primary_tags = _build_tag_norm_names(genre, subgenre)
    fallback_tags = _build_tag_norm_names(genre)
    attempts = [primary_tags]

    if primary_tags != fallback_tags:
        attempts.append(fallback_tags)
    if fallback_tags:
        attempts.append([])

    with requests.Session() as session:
        attempted_pages = []
        api_requests_made = 0
        for index, tag_norm_names in enumerate(attempts, start=1):
            page_label = _format_page_label(tag_norm_names)
            attempted_pages.append(page_label)
            batch = _fetch_discover(session, tag_norm_names, size)
            api_requests_made += 1
            urls = batch["urls"]
            api_page_count = batch["api_page_count"]

            urls = batch["urls"]
            if urls:
                metadata = {
                    "page_label": page_label,
                    "attempt_count": index,
                    "attempted_pages": attempted_pages,
                    "api_page_count": api_page_count,
                    "api_page_number": 1,
                    "api_page_range": [1, api_page_count or 1],
                    "api_requests_made": api_requests_made,
                    "result_count": batch["result_count"],
                }
                return urls, metadata

    raise NoDiscoverResultsError(
        "Bandcamp Discover returned no playable results for the provided tags"
    )
