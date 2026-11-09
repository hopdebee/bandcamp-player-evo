# coding=utf-8
import os
import unittest
from unittest import mock

from bandcamp_player.player import MpvController, PlaybackError


class GetPropertyTests(unittest.TestCase):
    def test_get_property_returns_default_when_unavailable(self):
        controller = MpvController()
        controller.connection = mock.Mock()
        controller._read_response = mock.Mock(
            return_value={"error": "property unavailable", "data": None}
        )

        value = controller.get_property("time-pos", default=None)

        self.assertIsNone(value)

    def test_get_property_returns_data_on_success(self):
        controller = MpvController()
        controller.connection = mock.Mock()
        controller._read_response = mock.Mock(
            return_value={"error": "success", "data": 42}
        )

        value = controller.get_property("volume", default=None)

        self.assertEqual(value, 42)


class PlaylistTests(unittest.TestCase):
    def test_loads_direct_stream_playlist_and_cleans_up_files(self):
        controller = MpvController()
        controller.command = mock.Mock()
        self.addCleanup(controller.close)
        tracks = [
            {"title": "First\ntrack", "url": "https://t4.bcbits.com/first?x=1&y=2"},
            {"title": "Second", "url": "https://t4.bcbits.com/second"},
        ]
        with mock.patch("bandcamp_player.player.album_stream_tracks", return_value=tracks):
            controller.load("https://artist.bandcamp.com/album/example")
            first_playlist = controller._playlist_path
            with open(first_playlist, encoding="utf-8") as playlist:
                self.assertEqual(
                    playlist.read(),
                    "#EXTM3U\n#EXTINF:-1,First track\nhttps://t4.bcbits.com/first?x=1&y=2\n"
                    "#EXTINF:-1,Second\nhttps://t4.bcbits.com/second\n",
                )
            controller.command.assert_called_once_with("loadlist", first_playlist, "replace")
            controller.load("https://artist.bandcamp.com/album/other")
            second_playlist = controller._playlist_path

        self.assertFalse(os.path.exists(first_playlist))
        self.assertTrue(os.path.exists(second_playlist))
        controller.close()
        self.assertFalse(os.path.exists(second_playlist))


class PlaybackEventTests(unittest.TestCase):
    def test_load_failure_surfaces_mpv_error_and_log_messages(self):
        controller = MpvController()
        controller.connection = mock.Mock()
        controller._read_message = mock.Mock(side_effect=[
            {"event": "log-message", "prefix": "ffmpeg", "text": "HTTP error 403 Forbidden\n"},
            {"event": "end-file", "reason": "error", "file_error": "loading failed"},
            {"request_id": 1, "error": "success", "data": True},
        ])

        with self.assertRaisesRegex(PlaybackError, "loading failed") as error:
            controller.is_idle()

        self.assertIn("HTTP error 403 Forbidden", str(error.exception))

    def test_file_loaded_and_normal_eof_are_not_errors(self):
        controller = MpvController()
        controller.connection = mock.Mock()
        controller._read_message = mock.Mock(side_effect=[
            {"event": "file-loaded"},
            {"event": "end-file", "reason": "eof"},
            {"request_id": 1, "error": "success", "data": True},
        ])

        self.assertTrue(controller.is_idle())
        self.assertTrue(controller.has_loaded_file)
