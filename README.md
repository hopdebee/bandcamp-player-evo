bandcamp-player-evo
============

streaming random music from bandcamp by specified genre subgenre inspired on https://github.com/strizhechenko/bandcamp-player

![](bandcamp-player-evo_demo.gif)

Usage
=====

``bandcamp-player-evo ["genre"] ["sub genre"]``

Genres can be found on the bandcamp homepage. Slashes spaces and &'s in the genre name should be replaced by dashes (hip-hop/rap becomes hip-hop-rap r&b/soul becomes r-b-soul, field recordings becomes field-recordings). If a certain genre subgenre combo does not work, bandcamp-fetch gets you a random album from the "all" category. You can enter "" as the second argument in order to play from all subgenres of that genre. This equates to "all-genre". Check more genre values in https://github.com/patrickkfkan/bandcamp-fetch/blob/867dd856c9865b716cddce73cd7a8ccd6b03309b/examples/discovery/getAvailableOptions_output.txt#L1411

MPV

check https://mpv.io/manual/master/ for keyboard controls of the mpv cli music player (eg arrows to scrub, ">" to go to next track)

Installation
============
install node and npm https://nodejs.org/en/download/, tutorial (https://radixweb.com/blog/installing-npm-and-nodejs-on-windows-and-mac)

install python version 3.4 or above+

install mpv (https://mpv.io/installation/)

install bandcamp-fetch (https://github.com/patrickkfkan/bandcamp-fetch ) with

``npm i bandcamp-fetch --save``

``cd`` into the ``bandcamp-player-evo`` folder

assuming you have cloned ``bandcamp-player-evo`` in your home folder:

Test it by running ``node ~/bandcamp-player-evo/bandcamp_parser/scrape.js "." "ambient" "drone"`` if no error is given and the albums.json file in ``/bandcamp_parser`` has in it's results the correct ambient and drone ``params``, you're good to go.

make sure again you are in the folder you downloaded from github

from your home folder: 

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
