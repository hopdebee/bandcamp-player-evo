# coding=utf-8
"""Terminal input helpers for interactive playback controls."""

from __future__ import annotations

import os
import select
import sys
import termios
import tty

from bandcamp_player.controls import translate_escape_sequence


class TerminalInput(object):
    """Read single keys from a terminal without waiting for Enter."""

    def __init__(self, stream=None):
        self.stream = stream or sys.stdin
        self.fd = self.stream.fileno()
        self._settings = None

    def __enter__(self):
        self._settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._settings is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self._settings)

    def read_key(self, timeout=0.2):
        """Read one key or escape sequence, or return None on timeout."""
        ready, _write, _error = select.select([self.fd], [], [], timeout)
        if not ready:
            return None

        first = os.read(self.fd, 1)
        if first == b"\x03":
            raise KeyboardInterrupt
        if first == b"\x1b":
            sequence = self._read_escape_sequence()
            return translate_escape_sequence(sequence)

        try:
            return first.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def _read_escape_sequence(self):
        sequence = b""
        while True:
            ready, _write, _error = select.select([self.fd], [], [], 0.01)
            if not ready:
                break
            sequence += os.read(self.fd, 1)
        return sequence


class NullInput(object):
    """Fallback input router for non-interactive environments."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def read_key(self, timeout=0.2):
        select.select([], [], [], timeout)
        return None
