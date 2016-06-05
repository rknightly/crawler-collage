# crawler-collage
A collage-making web crawler

This is a web crawler that starts at a url given by the user
and takes all of the images from that page. Then, the crawler
visits every link on that page and collects all of those images.
This continues until the page limit is reached or a complete dead-end
is hit.

Finally, a collage is made with all of the images found.

The collage maker was adapted from delimitry's version at 
https://github.com/delimitry/collage_maker so thanks to him for allowing
the use of his collage maker. Note that I did have to update it to 
Python 3 and add additional features to make it work with my program,
but the base algorithm is still the same. 
