# coding=utf-8
import logging
import shutil
import time
import sys

from bandcamp_parser.tag import Tag
from bandcamp_player.controls import CONTROL_HELP, action_for_key
from bandcamp_player.player import MpvController
from bandcamp_player.status import render_progress_line
from bandcamp_player.terminal import NullInput, TerminalInput

logging.basicConfig(level=logging.INFO)
LOAD_START_TIMEOUT_SECONDS = 5
PROGRESS_REFRESH_SECONDS = 0.25


def _clear_status_line():
    """Clear the current terminal status line."""
    width = shutil.get_terminal_size((80, 20)).columns
    sys.stdout.write("\r" + (" " * max(width - 1, 1)) + "\r")
    sys.stdout.flush()


def _print_event_line(message, interactive=False):
    """Print a normal event line without corrupting the live status line."""
    if interactive:
        _clear_status_line()
    print(message)


def _show_progress(player):
    """Render the current track progress in place."""
    progress = player.get_progress()
    width = shutil.get_terminal_size((80, 20)).columns
    line = render_progress_line(progress)
    padded = line[: max(width - 1, 1)].ljust(max(width - 1, 1))
    sys.stdout.write("\r" + padded)
    sys.stdout.flush()


def _sample_summary(tag_data):
    """Build a one-line summary of the sampled album pool."""
    upper_range_end = tag_data.last_sample_meta.get("api_page_range", [1, 1])[1]
    page_label = tag_data.last_sample_page or "all"
    return "randomly sampled from {0} {1} albums".format(
        upper_range_end, page_label
    )


def _start_next_album(tag_data, player, interactive=False):
    """Sample and load the next album into the long-lived mpv process."""
    album_url = tag_data.album_random()
    _print_event_line(
        _sample_summary(tag_data),
        interactive=interactive,
    )
    _print_event_line(
        "playing from album {0}".format(album_url), interactive=interactive
    )
    player.load(album_url)
    return time.time()


def _handle_keypress(key, player):
    """Route one key press to either app logic or mpv IPC."""
    action, payload = action_for_key(key)
    if action == "album_next":
        return "album_next"
    if action == "quit":
        return "quit"
    if action == "mpv":
        player.command(*payload)
    return None


def loop():
    """Play albums forever until the user quits."""
    tag_data = Tag(sys.argv[1], sys.argv[2])
    player = MpvController().start()
    interactive = sys.stdin.isatty()
    input_router = TerminalInput() if interactive else NullInput()
    if interactive:
        print(CONTROL_HELP)
    album_loaded_at = _start_next_album(tag_data, player, interactive=interactive)
    has_started_current_album = False
    last_progress_at = 0

    try:
        with input_router as terminal:
            while True:
                if not player.is_alive():
                    raise RuntimeError("mpv exited unexpectedly")

                idle = player.is_idle()
                if not idle:
                    has_started_current_album = True
                    if interactive and time.time() - last_progress_at >= PROGRESS_REFRESH_SECONDS:
                        _show_progress(player)
                        last_progress_at = time.time()
                elif has_started_current_album:
                    album_loaded_at = _start_next_album(
                        tag_data, player, interactive=interactive
                    )
                    has_started_current_album = False
                    last_progress_at = 0
                    continue
                elif time.time() - album_loaded_at > LOAD_START_TIMEOUT_SECONDS:
                    album_loaded_at = _start_next_album(
                        tag_data, player, interactive=interactive
                    )
                    has_started_current_album = False
                    last_progress_at = 0
                    continue

                key = terminal.read_key(timeout=0.2)
                if key is None:
                    continue

                result = _handle_keypress(key, player)
                if result == "quit":
                    if interactive:
                        _clear_status_line()
                    return
                if result == "album_next":
                    album_loaded_at = _start_next_album(
                        tag_data, player, interactive=interactive
                    )
                    has_started_current_album = False
                    last_progress_at = 0
    finally:
        if interactive:
            _clear_status_line()
        player.close()


def main():
    """ Playing the tracks until CTRL-C """
    try:
        loop()
    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    main()
