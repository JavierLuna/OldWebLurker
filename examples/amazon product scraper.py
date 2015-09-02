__author__ = 'jluna'
from WebLurker import WebLurker
import re

"""
Gets a list of products from a search on amazon.es
It uses regex extractors
I know, I'm not a python ninja... YET!
"""

base_url = "http://www.amazon.es/s/ref=nb_sb_noss_2?__mk_es_ES=ÅMÅŽÕÑ&url=search-alias%3Daps&field-keywords="+input("Search somethin' yo\n:>").replace(" ","+")
wl = WebLurker()
wl.feed(base_url)
wl.addExtractor(re.compile(r'<h2 class="a-size-medium a-color-null s-inline s-access-title a-text-normal">(.*?)</h2>',re.S|re.M), "item")
wl.lurk()
print(wl.getRefinedData())
for page in wl.getRefinedData():
    for elemento in wl.getRefinedData()[page]["item"]:
        print(elemento)
