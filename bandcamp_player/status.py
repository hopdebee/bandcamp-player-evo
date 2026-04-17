# coding=utf-8
"""Helpers for formatting live playback status."""


def format_seconds(value):
    """Format a second count as mm:ss or hh:mm:ss."""
    if value is None:
        return "--:--"

    total_seconds = max(int(value), 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours:
        return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
    return "{0:02d}:{1:02d}".format(minutes, seconds)


def render_progress_line(progress):
    """Render one human-readable playback progress line."""
    title = progress.get("media_title") or "unknown title"
    percent = progress.get("percent_pos")
    if percent is None:
        percent_text = "--%"
    else:
        percent_text = "{0:>3.0f}%".format(percent)

    state = "paused" if progress.get("pause") else "playing"
    return "{0} / {1} ({2}) | {3} | {4}".format(
        format_seconds(progress.get("time_pos")),
        format_seconds(progress.get("duration")),
        percent_text,
        state,
        title,
    )
