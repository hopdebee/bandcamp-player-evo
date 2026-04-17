# coding=utf-8
import logging
import sys

from bandcamp_parser.tag import Tag
from bandcamp_parser.track import Track

logging.basicConfig(level=logging.INFO)


def loop():
    """ Playing tracks in infinite loop """
    tag_data = Tag(sys.argv[1], sys.argv[2]) 
    while True:
        album_url = tag_data.album_random()
        print(f"sampled from page {tag_data.last_sample_page}")
        print(
            "discover api page range: "
            f"{tag_data.last_sample_meta.get('api_page_range', [1, 1])[0]}-"
            f"{tag_data.last_sample_meta.get('api_page_range', [1, 1])[1]}, "
            f"sampled page {tag_data.last_sample_meta.get('api_page_number', 1)}"
        )
        print(
            "api requests made: "
            f"{tag_data.last_sample_meta.get('api_requests_made', 0)}; source pages tried: "
            f"{tag_data.last_sample_meta.get('attempt_count', 0)} "
            f"({', '.join(tag_data.last_sample_meta.get('attempted_pages', []))})"
        )
        print(f"playing from album {album_url}")
        track = Track(album_url)
        track.play()


def main():
    """ Playing the tracks until CTRL-C """
    try:
        loop()
    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    main()
