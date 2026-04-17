# coding=utf-8
import unittest

from bandcamp_player.controls import action_for_key, translate_escape_sequence


class EscapeSequenceTests(unittest.TestCase):
    def test_translate_arrow_keys(self):
        self.assertEqual(translate_escape_sequence(b"[A"), "UP")
        self.assertEqual(translate_escape_sequence(b"[B"), "DOWN")
        self.assertEqual(translate_escape_sequence(b"[C"), "RIGHT")
        self.assertEqual(translate_escape_sequence(b"[D"), "LEFT")

    def test_translate_unknown_escape_sequence(self):
        self.assertEqual(translate_escape_sequence(b"[1;5A"), None)


class ActionRoutingTests(unittest.TestCase):
    def test_album_next_key(self):
        self.assertEqual(action_for_key("n"), ("album_next", None))

    def test_quit_key(self):
        self.assertEqual(action_for_key("q"), ("quit", None))

    def test_pause_key(self):
        self.assertEqual(action_for_key(" "), ("mpv", ("cycle", "pause")))

    def test_track_navigation_keys(self):
        self.assertEqual(
            action_for_key(">"), ("mpv", ("playlist-next", "force"))
        )
        self.assertEqual(
            action_for_key("<"), ("mpv", ("playlist-prev", "force"))
        )

    def test_seek_and_volume_keys(self):
        self.assertEqual(action_for_key("RIGHT"), ("mpv", ("seek", "5")))
        self.assertEqual(action_for_key("LEFT"), ("mpv", ("seek", "-5")))
        self.assertEqual(action_for_key("UP"), ("mpv", ("add", "volume", "5")))
        self.assertEqual(action_for_key("DOWN"), ("mpv", ("add", "volume", "-5")))
        self.assertEqual(action_for_key("9"), ("mpv", ("add", "volume", "-2")))
        self.assertEqual(action_for_key("0"), ("mpv", ("add", "volume", "2")))

    def test_mute_key(self):
        self.assertEqual(action_for_key("m"), ("mpv", ("cycle", "mute")))

    def test_unknown_key(self):
        self.assertEqual(action_for_key("x"), (None, None))
