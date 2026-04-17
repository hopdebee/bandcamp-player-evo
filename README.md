bandcamp-player-evo
===================

Stream random Bandcamp releases by genre and subgenre from the command line.

This version is Python-only. It no longer depends on Node.js, `npm`, or `bandcamp-fetch`. Instead, it talks directly to Bandcamp's Discover API from Python.

![](bandcamp-player-evo_demo.gif)

Usage
=====

``bandcamp-player-evo ["genre"] ["sub genre"]``

Example:

``uv run bandcamp-player-evo ambient drone``

Genres and subgenres follow Bandcamp's normalized tag format. Replace spaces, slashes, and `&` with dashes:

- `hip-hop/rap` -> `hip-hop-rap`
- `r&b/soul` -> `r-b-soul`
- `field recordings` -> `field-recordings`

If a genre/subgenre combination returns no results, the player falls back in this order:

1. `genre + subgenre`
2. `genre`
3. `all`

You can pass an empty second argument to use only the genre:

``uv run bandcamp-player-evo ambient ""``

How It Works
============

The app sends a Python `requests` POST to:

``https://bandcamp.com/api/discover/1/discover_web``

using a payload like:

```json
{
  "category_id": 0,
  "cursor": "*",
  "geoname_id": 0,
  "include_result_types": ["a", "s"],
  "size": 1,
  "slice": "rand",
  "tag_norm_names": ["ambient", "drone"],
  "time_facet_id": null
}
```

At runtime, the CLI:

- prints a sampling summary such as `randomly sampled album from (154398) ambient/drone albums`
- how many API requests were made, including fallback attempts
- sends the sampled Bandcamp album URL to a long-lived `mpv` process over JSON IPC
- shows a live in-place progress line with current position, duration, pause state, and track title

Requirements
============

- `uv`
- `mpv`

`mpv` is required because the CLI opens the sampled Bandcamp release URL with it.

Interactive Controls
====================

The player keeps a single `mpv` process alive and controls it over `mpv`'s JSON IPC socket. Python owns the terminal input, so it can reserve album-level hotkeys while still forwarding common playback controls to `mpv`.

Application-level keys:

- `n` loads the next random album
- `q` quits the app cleanly
- `Ctrl-C` stops the app immediately

Playback keys routed to `mpv` over IPC:

- `>` next track
- `<` previous track
- `space` pause or resume
- `left` seek backward 5 seconds
- `right` seek forward 5 seconds
- `up` volume up 5
- `down` volume down 5
- `9` volume down 2
- `0` volume up 2
- `m` mute toggle

When an album finishes, Python detects that `mpv` is idle and automatically samples the next album.

In an interactive terminal, the player also shows a live status line such as:

```text
02:14 / 07:31 ( 29%) | playing | Example Track
```

This line is updated in place while the track plays.

Local Development
=================

Clone the repo, then from the project root:

``uv sync``

Run tests:

``uv run python -m unittest discover -s tests -v``

Run the CLI:

``uv run bandcamp-player-evo ambient drone``

The CLI will print the active control bindings when it starts.

If you want to inspect the selection logic without launching `mpv`, you can run:

```bash
uv run python - <<'PY'
from bandcamp_parser.tag import Tag

tag = Tag("ambient", "drone")
print(tag.album_random())
print(tag.last_sample_meta)
PY
```

Try With `uvx`
==============

From the repo folder:

``uvx --from . bandcamp-player-evo ambient drone``

From another machine:

``uvx --from git+https://github.com/hopdebee/bandcamp-player-evo.git bandcamp-player-evo ambient drone``

This requires `uv` and `mpv` to be installed on the target machine.

Persistent Install With `uv tool`
=================================

To install the CLI persistently from the repo folder:

``uv tool install .``

To install it persistently from Git:

``uv tool install --from git+https://github.com/<you>/<repo>.git bandcamp-player-evo``

Then run it with:

``bandcamp-player-evo ambient drone``

To update or reinstall from the current repo:

``uv tool install --force .``

To remove it:

``uv tool uninstall bandcamp-player-evo``

Termux
======

Install the required packages:

``pkg install uv mpv git``

Run directly from Git with `uvx`:

``uvx --from git+https://github.com/<you>/<repo>.git bandcamp-player-evo ambient drone``

Or clone and run locally:

``git clone https://github.com/<you>/<repo>.git``

``cd <repo>``

``uv run bandcamp-player-evo ambient drone``

MPV
===

See the `mpv` manual for playback controls:

https://mpv.io/manual/master/

Bugs
====

Open an issue if Bandcamp changes its Discover API behavior or if a particular tag combination consistently fails unexpectedly.
