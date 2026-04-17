# coding=utf-8
"""Keyboard routing for album- and mpv-level controls."""


CONTROL_HELP = (
    "controls: n next album | > next track | < previous track | space pause | "
    "left/right seek | up/down volume | 9/0 volume | m mute | q quit | Ctrl-C stop"
)


def translate_escape_sequence(sequence):
    """Translate terminal escape sequences into symbolic key names."""
    mapping = {
        b"[A": "UP",
        b"[B": "DOWN",
        b"[C": "RIGHT",
        b"[D": "LEFT",
    }
    return mapping.get(sequence)


def action_for_key(key):
    """Map a key press to an application or mpv action."""
    if key == "n":
        return ("album_next", None)
    if key == "q":
        return ("quit", None)

    command_map = {
        " ": ("cycle", "pause"),
        ">": ("playlist-next", "force"),
        "<": ("playlist-prev", "force"),
        "RIGHT": ("seek", "5"),
        "LEFT": ("seek", "-5"),
        "UP": ("add", "volume", "5"),
        "DOWN": ("add", "volume", "-5"),
        "9": ("add", "volume", "-2"),
        "0": ("add", "volume", "2"),
        "m": ("cycle", "mute"),
    }
    command = command_map.get(key)
    if command:
        return ("mpv", command)
    return (None, None)
