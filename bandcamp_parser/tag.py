# coding=utf-8
from random import shuffle
# 
# from bs4 import BeautifulSoup
import os
import json
class Tag(object):
    """ Provides access to album list by specified genre/subgenre """

    def __init__(self, genre, subgenre):
        self.genre = genre
        self.subgenre = subgenre

    def albums(self) -> list:
        """ :returns: list of Albums from random genre/subgenre page """

        os.system(f"node /home/heopd/bandcamp-player/bandcamp_parser/scrape.js {self.genre} {self.subgenre}")
        with open("/home/heopd/bandcamp-player/bandcamp_parser/albums.json", encoding='utf-8') as f:
            results = json.load(f)
        
        albumurls = [res["url"] for res in results["items"]]
        try:
            results["params"]["subgenre"]
        except:
            results["params"]["subgenre"] = "no subgenre"
        print(f"picking random album out of {str(len(albumurls))} albums from page {str(results['params']['page'])} in the category {str(results['params']['genre']), str(results['params']['subgenre'])}")
        return albumurls

    def album_random(self):# -> AlbumResult:
        """ :returns: random Album from random genre/subgenre page """
        albums = self.albums()
        shuffle(albums)
        return albums[0]
