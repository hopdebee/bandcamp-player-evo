# coding=utf-8
import io
import unittest
from unittest import mock

import bandcamp_player
from bandcamp_parser.album import AlbumLoadError
from bandcamp_player.player import PlaybackError


class PlaybackLoopTests(unittest.TestCase):
    def setUp(self):
        self.player = mock.Mock()
        self.player.has_loaded_file = False
        self.player.is_alive.return_value = True
        patches = [
            mock.patch.object(bandcamp_player.sys, "argv", ["bandcamp-player-evo", "ambient", "field-recordings"]),
            mock.patch.object(bandcamp_player.sys.stdin, "isatty", return_value=False),
            mock.patch.object(bandcamp_player, "Tag"),
            mock.patch.object(bandcamp_player, "MpvController"),
            mock.patch.object(bandcamp_player, "_start_next_album", return_value=0),
            mock.patch.object(bandcamp_player, "NullInput"),
        ]
        self.mocks = [patch.start() for patch in patches]
        for patch in patches:
            self.addCleanup(patch.stop)
        self.mocks[3].return_value.start.return_value = self.player
        self.start_album = self.mocks[4]
        self.terminal = self.mocks[5].return_value.__enter__.return_value

    def test_initial_album_failure_closes_player(self):
        self.start_album.side_effect = AlbumLoadError("No public streams")
        with self.assertRaises(AlbumLoadError):
            bandcamp_player.loop()
        self.player.close.assert_called_once_with()

    def test_mpv_failure_stops_without_sampling_another_album(self):
        self.player.is_idle.side_effect = PlaybackError("HTTP 403")
        with self.assertRaisesRegex(PlaybackError, "HTTP 403"):
            bandcamp_player.loop()
        self.start_album.assert_called_once()
        self.player.close.assert_called_once_with()

    def test_load_timeout_stops_instead_of_skipping(self):
        for idle in (True, False):
            with self.subTest(idle=idle):
                self.player.is_idle.return_value = idle
                self.start_album.reset_mock()
                with mock.patch.object(bandcamp_player.time, "time", return_value=31):
                    with self.assertRaisesRegex(PlaybackError, "did not start playback"):
                        bandcamp_player.loop()
                self.start_album.assert_called_once()

    def test_finished_album_still_advances_automatically(self):
        self.player.has_loaded_file = True
        self.player.is_idle.side_effect = [False, True, False]
        self.terminal.read_key.side_effect = [None, "q"]
        bandcamp_player.loop()
        self.assertEqual(self.start_album.call_count, 2)
        self.player.close.assert_called_once_with()

    def test_loading_is_not_treated_as_a_finished_album(self):
        self.player.is_idle.side_effect = [False, True, False]
        self.terminal.read_key.side_effect = [None, None, "q"]
        with mock.patch.object(bandcamp_player.time, "time", return_value=6):
            bandcamp_player.loop()
        self.start_album.assert_called_once()
        self.player.close.assert_called_once_with()

    def test_main_reports_playback_error_and_returns_failure(self):
        with mock.patch.object(bandcamp_player, "loop", side_effect=PlaybackError("HTTP 403")):
            with mock.patch.object(bandcamp_player.sys, "stderr", new_callable=io.StringIO) as stderr:
                self.assertEqual(bandcamp_player.main(), 1)
        self.assertEqual(stderr.getvalue(), "error: HTTP 403\n")
