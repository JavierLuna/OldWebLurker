__author__ = 'jluna'
import re

from WebLurker import WebLurker


"""
Get list of products from search on amazon.es
It uses regex extractors
I know, I'm not a python ninja... YET!
"""

base_url = "http://www.amazon.es/s/ref=nb_sb_noss_2?__mk_es_ES=ÅMÅŽÕÑ&url=search-alias%3Daps&field-keywords=" + input(
    "Search somethin' yo\n:>").replace(" ", "+")
wl = WebLurker()
wl.feed(base_url)
wl.addExtractor(
    re.compile(r'<h2 class="a-size-medium a-color-null s-inline s-access-title a-text-normal">(.*?)</h2>', re.S | re.M),
    "item")
wl.lurk()
for item in wl.query(wl.getRefinedData(), base_url, "item"):
    print(item)