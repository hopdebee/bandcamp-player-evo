# coding=utf-8
from random import shuffle

from bandcamp_parser.discover import discover_album_urls_with_source


class Tag(object):
    """ Provides access to album list by specified genre/subgenre """

    def __init__(self, genre, subgenre):
        self.genre = genre
        self.subgenre = subgenre
        self.last_sample_page = None
        self.last_sample_meta = {}

    def albums(self):
        """ :returns: list of Albums from random genre/subgenre page """
        albums, metadata = discover_album_urls_with_source(self.genre, self.subgenre)
        self.last_sample_page = metadata["page_label"]
        self.last_sample_meta = metadata
        return albums

    def album_random(self):# -> AlbumResult:
        """ :returns: random Album from random genre/subgenre page """
        albums = self.albums()
        shuffle(albums)
        return albums[0]
