# Playback extraction maintenance

If Bandcamp changes break direct stream parsing and a straightforward repair does not work, you must reconsider using yt-dlp before continuing to expand or patch the custom parser.

- Check the latest yt-dlp release and test it against the failing release URL, with any dependencies required by its Bandcamp extractor.
- Compare that result with direct parsing. If yt-dlp works and direct parsing remains unreliable, prefer switching extraction to yt-dlp.
- Record the tested yt-dlp version and result. The original failure was reproduced with version 2026.08.19; the latest version was not tested then. That failure is not evidence that newer versions cannot handle Bandcamp.
