# coding=utf-8
import unittest

from bandcamp_player.status import format_seconds, render_progress_line


class FormatSecondsTests(unittest.TestCase):
    def test_none(self):
        self.assertEqual(format_seconds(None), "--:--")

    def test_minutes(self):
        self.assertEqual(format_seconds(125), "02:05")

    def test_hours(self):
        self.assertEqual(format_seconds(3723), "01:02:03")


class RenderProgressLineTests(unittest.TestCase):
    def test_render_progress_line(self):
        line = render_progress_line(
            {
                "time_pos": 125,
                "duration": 300,
                "percent_pos": 41.6,
                "pause": False,
                "media_title": "Example Track",
            }
        )
        self.assertIn("02:05 / 05:00", line)
        self.assertIn("( 42%)", line)
        self.assertIn("playing", line)
        self.assertIn("Example Track", line)

    def test_render_progress_line_with_missing_values(self):
        line = render_progress_line(
            {
                "time_pos": None,
                "duration": None,
                "percent_pos": None,
                "pause": True,
                "media_title": None,
            }
        )
        self.assertIn("--:-- / --:--", line)
        self.assertIn("(--)".replace(")", "%)"), line)
        self.assertIn("paused", line)
        self.assertIn("unknown title", line)
