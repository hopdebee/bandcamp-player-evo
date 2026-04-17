# coding=utf-8
import unittest
from unittest import mock

from bandcamp_player.player import MpvController


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
