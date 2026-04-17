# coding=utf-8
import unittest
from unittest import mock

from bandcamp_parser import discover


class BuildPayloadTests(unittest.TestCase):
    def test_build_tag_norm_names_genre_only(self):
        self.assertEqual(discover._build_tag_norm_names("ambient"), ["ambient"])

    def test_build_tag_norm_names_genre_and_subgenre(self):
        self.assertEqual(
            discover._build_tag_norm_names("ambient", "drone"),
            ["ambient", "drone"],
        )

    def test_build_tag_norm_names_empty_subgenre(self):
        self.assertEqual(discover._build_tag_norm_names("ambient", ""), ["ambient"])

    def test_build_payload(self):
        self.assertEqual(
            discover._build_payload(["ambient", "drone"], size=2),
            {
                "category_id": 0,
                "cursor": "*",
                "geoname_id": 0,
                "include_result_types": ["a", "s"],
                "size": 2,
                "slice": "rand",
                "tag_norm_names": ["ambient", "drone"],
                "time_facet_id": None,
            },
        )

    def test_build_payload_with_cursor(self):
        self.assertEqual(
            discover._build_payload(["ambient"], size=2, cursor="abc"),
            {
                "category_id": 0,
                "cursor": "abc",
                "geoname_id": 0,
                "include_result_types": ["a", "s"],
                "size": 2,
                "slice": "rand",
                "tag_norm_names": ["ambient"],
                "time_facet_id": None,
            },
        )

    def test_format_page_label(self):
        self.assertEqual(discover._format_page_label(["ambient", "drone"]), "ambient/drone")
        self.assertEqual(discover._format_page_label(["ambient"]), "ambient")
        self.assertEqual(discover._format_page_label([]), "all")

    def test_parse_discover_batch(self):
        batch = discover._parse_discover_batch(
            {
                "result_count": 5,
                "results": [
                    {"item_url": "https://artist.bandcamp.com/album/example?from=discover_page"}
                ],
            },
            size=2,
        )

        self.assertEqual(batch["urls"], ["https://artist.bandcamp.com/album/example"])
        self.assertEqual(batch["result_count"], 5)
        self.assertEqual(batch["api_page_count"], 3)
        self.assertEqual(batch["cursor"], None)


class ParseResultsTests(unittest.TestCase):
    def test_extract_album_urls_ignores_malformed_items(self):
        data = {
            "results": [
                {"item_url": "https://artist.bandcamp.com/album/example?from=discover_page"},
                {"item_url": "https://artist.bandcamp.com/merch/shirt"},
                {"band_name": "missing url"},
            ]
        }

        self.assertEqual(
            discover._extract_album_urls(data),
            ["https://artist.bandcamp.com/album/example"],
        )


class DiscoverFallbackTests(unittest.TestCase):
    def test_discover_album_urls_with_source_returns_page_label(self):
        with mock.patch.object(
            discover,
            "_fetch_discover",
            side_effect=[
                {
                    "urls": ["https://a.bandcamp.com/album/x"],
                    "result_count": 10,
                    "api_page_count": 10,
                    "cursor": "next",
                }
            ],
        ):
            urls, metadata = discover.discover_album_urls_with_source("ambient", "drone")

        self.assertEqual(urls, ["https://a.bandcamp.com/album/x"])
        self.assertEqual(metadata["page_label"], "ambient/drone")
        self.assertEqual(metadata["api_page_count"], 10)
        self.assertEqual(metadata["api_page_number"], 1)

    def test_first_request_succeeds(self):
        with mock.patch.object(
            discover,
            "_fetch_discover",
            side_effect=[
                {
                    "urls": ["https://a.bandcamp.com/album/x"],
                    "result_count": 10,
                    "api_page_count": 10,
                    "cursor": "next",
                }
            ],
        ) as fetch:
            urls = discover.discover_album_urls("ambient", "drone")

        self.assertEqual(urls, ["https://a.bandcamp.com/album/x"])
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(fetch.call_args_list[0][0][1], ["ambient", "drone"])

    def test_subgenre_fallback_to_genre(self):
        with mock.patch.object(
            discover,
            "_fetch_discover",
            side_effect=[
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
                {
                    "urls": ["https://a.bandcamp.com/album/x"],
                    "result_count": 20,
                    "api_page_count": 20,
                    "cursor": "next",
                },
            ],
        ) as fetch:
            urls, metadata = discover.discover_album_urls_with_source(
                "ambient", "bad-subgenre"
            )

        self.assertEqual(urls, ["https://a.bandcamp.com/album/x"])
        self.assertEqual(metadata["page_label"], "ambient")
        self.assertEqual(metadata["attempt_count"], 2)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(fetch.call_args_list[0][0][1], ["ambient", "bad-subgenre"])
        self.assertEqual(fetch.call_args_list[1][0][1], ["ambient"])

    def test_genre_fallback_to_global(self):
        with mock.patch.object(
            discover,
            "_fetch_discover",
            side_effect=[
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
                {
                    "urls": ["https://a.bandcamp.com/album/x"],
                    "result_count": 30,
                    "api_page_count": 30,
                    "cursor": "next",
                },
            ],
        ) as fetch:
            urls, metadata = discover.discover_album_urls_with_source(
                "bad-genre", "bad-subgenre"
            )

        self.assertEqual(urls, ["https://a.bandcamp.com/album/x"])
        self.assertEqual(metadata["page_label"], "all")
        self.assertEqual(metadata["attempted_pages"], ["bad-genre/bad-subgenre", "bad-genre", "all"])
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(fetch.call_args_list[2][0][1], [])

    def test_all_attempts_empty_raise(self):
        with mock.patch.object(
            discover,
            "_fetch_discover",
            side_effect=[
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
                {
                    "urls": [],
                    "result_count": 0,
                    "api_page_count": 0,
                    "cursor": None,
                },
            ],
        ):
            with self.assertRaises(discover.NoDiscoverResultsError):
                discover.discover_album_urls("bad-genre", "bad-subgenre")
