# coding=utf-8
"""Long-lived mpv controller using JSON IPC."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import time
from collections import deque

from bandcamp_parser.album import album_stream_tracks


MPV_SOCKET_WAIT_SECONDS = 5


class PlaybackError(RuntimeError):
    """mpv could not load or play an audio stream."""


class MpvController(object):
    """Control a long-lived mpv process over JSON IPC."""

    def __init__(self):
        self.socket_path = os.path.join(
            tempfile.gettempdir(), "bandcamp-player-evo-{0}.sock".format(os.getpid())
        )
        self.process = None
        self.connection = None
        self._request_id = 0
        self._read_buffer = b""
        self._playlist_path = None
        self._playback_error = None
        self._log_messages = deque(maxlen=10)
        self.has_loaded_file = False

    def start(self):
        """Start mpv in idle mode and connect to its IPC socket."""
        self._cleanup_socket()
        self.process = subprocess.Popen(
            [
                "mpv",
                "--idle=yes",
                "--input-terminal=no",
                "--no-video",
                "--force-window=no",
                "--quiet",
                "--really-quiet",
                "--input-default-bindings=no",
                "--input-vo-keyboard=no",
                "--audio-display=no",
                "--ytdl=no",
                "--input-ipc-server={0}".format(self.socket_path),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            self._wait_for_socket()
            self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.connection.connect(self.socket_path)
            self._read_buffer = b""
            self.command("request_log_messages", "warn")
        except BaseException:
            self.close()
            raise
        return self

    def close(self):
        """Terminate mpv and clean up the IPC socket."""
        if self.connection is not None:
            try:
                self.command("quit")
            except Exception:
                pass
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None

        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=3)
            self.process = None

        self._cleanup_socket()
        self._cleanup_playlist()

    def command(self, *args):
        """Send an IPC command and return the decoded response."""
        if self.connection is None:
            raise RuntimeError("mpv IPC connection is not open")

        self._request_id += 1
        request_id = self._request_id
        payload = {"command": list(args), "request_id": request_id}
        self.connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        response = self._read_response(request_id)
        if response.get("error") not in ("success", None):
            raise RuntimeError(
                "mpv command failed: {0} ({1})".format(args, response.get("error"))
            )
        return response.get("data")

    def get_property(self, name, default=None):
        """Read one mpv property, returning default if it is unavailable."""
        if self.connection is None:
            raise RuntimeError("mpv IPC connection is not open")

        self._request_id += 1
        request_id = self._request_id
        payload = {"command": ["get_property", name], "request_id": request_id}
        self.connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        response = self._read_response(request_id)
        if response.get("error") == "success":
            return response.get("data")
        if response.get("error") == "property unavailable":
            return default
        raise RuntimeError(
            "mpv property failed: {0} ({1})".format(name, response.get("error"))
        )

    def load(self, url):
        """Resolve a release page and load its public streams as a playlist."""
        tracks = album_stream_tracks(url)
        self._cleanup_playlist()
        self._playback_error = None
        self._log_messages.clear()
        self.has_loaded_file = False
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".m3u8", delete=False
        ) as playlist:
            self._playlist_path = playlist.name
            playlist.write("#EXTM3U\n")
            for track in tracks:
                title = " ".join(track["title"].splitlines())
                playlist.write("#EXTINF:-1,{0}\n{1}\n".format(title, track["url"]))
        self.command("loadlist", self._playlist_path, "replace")

    def is_idle(self):
        """Return whether mpv is idle with no active file loaded."""
        idle = bool(self.command("get_property", "idle-active"))
        if self._playback_error:
            details = "\n".join(self._log_messages)
            raise PlaybackError(
                "mpv playback failed: {0}{1}".format(
                    self._playback_error, "\n" + details if details else ""
                )
            )
        return idle

    def is_alive(self):
        """Return whether the mpv subprocess is still running."""
        return self.process is not None and self.process.poll() is None

    def get_progress(self):
        """Return current playback progress properties from mpv."""
        return {
            "time_pos": self.get_property("time-pos"),
            "duration": self.get_property("duration"),
            "percent_pos": self.get_property("percent-pos"),
            "pause": bool(self.get_property("pause", default=False)),
            "media_title": self.get_property("media-title"),
        }

    def _read_response(self, request_id):
        while True:
            message = self._read_message()
            if message.get("request_id") == request_id:
                return message
            if message.get("event") == "file-loaded":
                self.has_loaded_file = True
            elif message.get("event") == "log-message":
                self._log_messages.append(
                    "[{0}] {1}".format(message.get("prefix", "mpv"), message.get("text", "").strip())
                )
            elif message.get("event") == "end-file" and message.get("reason") == "error":
                self._playback_error = message.get("file_error") or "unknown error"

    def _read_message(self):
        while b"\n" not in self._read_buffer:
            chunk = self.connection.recv(4096)
            if not chunk:
                raise RuntimeError("mpv IPC connection closed unexpectedly")
            self._read_buffer += chunk
        line, self._read_buffer = self._read_buffer.split(b"\n", 1)
        return json.loads(line.decode("utf-8"))

    def _wait_for_socket(self):
        deadline = time.time() + MPV_SOCKET_WAIT_SECONDS
        while time.time() < deadline:
            if os.path.exists(self.socket_path):
                return
            if self.process is not None and self.process.poll() is not None:
                raise RuntimeError("mpv exited before opening its IPC socket")
            time.sleep(0.05)
        raise RuntimeError("Timed out waiting for mpv IPC socket")

    def _cleanup_socket(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

    def _cleanup_playlist(self):
        if self._playlist_path is not None:
            if os.path.exists(self._playlist_path):
                os.unlink(self._playlist_path)
            self._playlist_path = None
