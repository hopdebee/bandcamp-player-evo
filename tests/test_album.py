# coding=utf-8
import html
import json
import unittest
from unittest import mock

import requests

from bandcamp_parser.album import AlbumLoadError, album_stream_tracks


ALBUM_URL = "https://artist.bandcamp.com/album/example"


class AlbumStreamTests(unittest.TestCase):
    def load_page(self, page):
        with mock.patch("bandcamp_parser.album.requests.get") as get:
            get.return_value.text = page
            tracks = album_stream_tracks(ALBUM_URL)
        get.assert_called_once_with(ALBUM_URL, timeout=20)
        get.return_value.raise_for_status.assert_called_once_with()
        return tracks

    def test_album_tracks_keep_order_and_decode_html_entities(self):
        data = {
            "trackinfo": [
                {"title": 'First & "quiet"', "file": {"mp3-128": "https://t4.bcbits.com/first?x=1&y=2"}},
                {"title": "Unavailable", "file": None},
                {"title": "Missing file"},
                {"title": "Second", "file": {"mp3-128": "//t4.bcbits.com/second"}},
            ]
        }
        page = '<script data-tralbum="{0}"></script>'.format(html.escape(json.dumps(data)))

        self.assertEqual(
            self.load_page(page),
            [
                {"title": 'First & "quiet"', "url": "https://t4.bcbits.com/first?x=1&y=2"},
                {"title": "Second", "url": "https://t4.bcbits.com/second"},
            ],
        )

    def test_single_track_release(self):
        data = {"trackinfo": [{"title": "Solo", "file": {"mp3-128": "https://t4.bcbits.com/solo"}}]}
        page = "<script data-tralbum='{0}'></script>".format(json.dumps(data))
        with mock.patch("bandcamp_parser.album.requests.get") as get:
            get.return_value.text = page
            tracks = album_stream_tracks("https://artist.bandcamp.com/track/solo")
        self.assertEqual(tracks, [{"title": "Solo", "url": "https://t4.bcbits.com/solo"}])

    def test_missing_or_invalid_track_data_reports_error(self):
        for page, message in [
            ("<title>Client Challenge</title>", "No track data"),
            ('<script data-tralbum="broken"></script>', "Invalid track data"),
            ('<script data-tralbum="null"></script>', "No track data"),
            ("<script data-tralbum='{}'></script>", "No publicly streamable tracks"),
        ]:
            with self.subTest(page=page):
                with self.assertRaisesRegex(AlbumLoadError, message):
                    self.load_page(page)

    def test_http_failure_includes_release_url(self):
        with mock.patch("bandcamp_parser.album.requests.get") as get:
            get.return_value.raise_for_status.side_effect = requests.HTTPError("503 unavailable")
            with self.assertRaisesRegex(AlbumLoadError, "503 unavailable") as error:
                album_stream_tracks(ALBUM_URL)
        self.assertIn(ALBUM_URL, str(error.exception))
