bandcamp-player
---------------

streaming random music from bandcamp by specified genre subgenre

![](bandcamp-player-evo_demo.gif)

usage
=====

``bandcamp-player-evo ["genre"] ["sub genre"]``


Installation
============
install node and npm https://nodejs.org/en/download/, tutorial (https://radixweb.com/blog/installing-npm-and-nodejs-on-windows-and-mac)

install python3.4+

install mpv (https://mpv.io/installation/)

install bandcamp-fetch (https://github.com/patrickkfkan/bandcamp-fetch ) with

``npm i bandcamp-fetch --save``

Test it by running ``node ~/bandcamp-player-evo/bandcamp_parser/scrape.js "ambient" "drone"``

make sure you are in the folder you downloaded from github

``cd bandcamp-player-evo``

install the package

``pip install -e .``

Description
===========

bandcamp-player is a small command-line app to stream audio from BandCamp.com. It requires the Python interpreter, version 3.4+.

You also need mpv installed.

You also need node installed (for scrape.js)

You also need https://github.com/patrickkfkan/bandcamp-fetch (for scrape.js)

Bugs
====

Bugs should be reported in the issues section
