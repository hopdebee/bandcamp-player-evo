const bcfetch = require('bandcamp-fetch');

//dunno if this works
bcfetch.cache.setTTL('page', 500);
bcfetch.cache.setMaxPages(20);

//define what you want and which page 
const params = {
    evopath: process.argv[2],
    genre: process.argv[3],
    subgenre: process.argv[4],
    sortBy: "rand",
    size: 1,

}

//get results and store in file
var fs = require('fs');
bcfetch.discovery.discover(params).then( results => {

    var json = JSON.stringify(results);
    fs.writeFile(params["evopath"]+"/bandcamp_parser/albums.json", json, function(err) {
        if (err) {
            console.log(err);
        }
    });
});


bcfetch.cache.clear('constant');

