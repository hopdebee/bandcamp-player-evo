# coding=utf-8
from random import shuffle
# 
# from bs4 import BeautifulSoup
import os
import json
import sys
import pprint 
class Tag(object):
    """ Provides access to album list by specified genre/subgenre """

    def __init__(self, genre, subgenre):
        self.genre = genre
        self.subgenre = subgenre

    def albums(self):
        """ :returns: list of Albums from random genre/subgenre page """
        evopath = [path for path in sys.path if "bandcamp-player-evo" in path][0]
        os.system(f"node {evopath}/bandcamp_parser/scrape.js {evopath} {self.genre} {self.subgenre}")
        with open(f"{evopath}/bandcamp_parser/albums.json", encoding='utf-8') as f:
            results = json.load(f)
        
        albumurls = [res["url"] for res in results["items"]]
        try:
            results["params"]["subgenre"]
        except:
            results["params"]["subgenre"] = "no subgenre"
        return albumurls

    def album_random(self):# -> AlbumResult:
        """ :returns: random Album from random genre/subgenre page """
        albums = self.albums()
        shuffle(albums)
        return albums[0]
