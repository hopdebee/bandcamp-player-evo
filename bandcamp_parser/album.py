# coding=utf-8
"""Read public audio streams from a Bandcamp release page."""

import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import requests

from bandcamp_parser.discover import REQUEST_TIMEOUT


class AlbumLoadError(RuntimeError):
    """A release page could not be resolved to playable streams."""


class _AlbumPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tralbum = None

    def handle_starttag(self, tag, attrs):
        value = dict(attrs).get("data-tralbum")
        if value is not None:
            self.tralbum = json.loads(value)


def album_stream_tracks(url):
    """Return stream URLs and titles in album order, excluding unstreamable tracks."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AlbumLoadError("Could not fetch {0}: {1}".format(url, exc)) from exc

    parser = _AlbumPageParser()
    try:
        parser.feed(response.text)
    except ValueError as exc:
        raise AlbumLoadError("Invalid track data on {0}".format(url)) from exc
    if not isinstance(parser.tralbum, dict):
        raise AlbumLoadError(
            "No track data on {0}; Bandcamp may have returned a verification page".format(url)
        )

    tracks = []
    for track in parser.tralbum.get("trackinfo") or []:
        files = track.get("file") or {}
        stream_url = files.get("mp3-128")
        if not stream_url:
            continue
        stream_url = urljoin(url, stream_url)
        parts = urlsplit(stream_url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            continue
        if "\n" in stream_url or "\r" in stream_url:
            continue
        tracks.append({"url": stream_url, "title": track.get("title") or "Untitled"})

    if not tracks:
        raise AlbumLoadError("No publicly streamable tracks on {0}".format(url))
    return tracks
