# coding=utf-8
import os

class Track(object):
    """ Provides a way to play music via mpv """

    def __init__(self, url):
        self.url = url

    def play(self) -> None:
        """ "stream" album via mpv """
        os.system("mpv " + self.url)
