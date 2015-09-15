__author__ = 'jluna'
import re

from WebLurker import WebLurker

wl = WebLurker(maxDepth=1, lapse=1, name="Mail extractor")
wl.feed("http://www.cunef.edu/")
wl.feed("http://www.apple.com/es/")
wl.addExtractor(re.compile('(?:[\w\-\.]+@(?:\w[\w\-]+\.)+[\w\-]+)'), "mail", clean=True)
wl.lurk()
print("Mails found:")
[print(item) for item in wl.query(wl.getRefinedData(), rootUrl="http://www.cunef.edu/", extractorId="mail")]
wl.toJSON()
