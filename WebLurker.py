from html.entities import name2codepoint
import re
import time
import json
import pickle
from os import listdir
from os.path import isfile, join
from html.parser import HTMLParser, HTMLParseError

import requests


__author__ = 'jluna'


class WebLurker():
    def __init__(self, maxDepth=0, lapse=0, quiet=False, name="WebLurker", headers={'User-Agent': 'Mozilla/5.0'}):
        self._maxDepth = maxDepth
        self._lapse = lapse
        self._quiet = quiet
        self._name = name

        self._maxDepth = maxDepth
        self._lapse = lapse

        self._quiet = quiet
        self._name = name

        self._root_webs = set()

        self._fExtractors = dict()
        self._rExtractors = dict()

        self._refiners = set()

        self._rawData = dict()
        self._extractedData = dict()
        self._refinedData = dict()

        self._domainBL = set()
        self._extensionBL = set()
        self._domainWL = set()
        self._extensionWL = set()

        self._headers = headers

    def feed(self, urls):
        if type(urls) is set:
            self._root_webs = self._root_webs.union(urls)
        elif type(urls) is str:
            self._root_webs.add(urls)
        else:
            self._root_webs = self._root_webs.union(set(urls))

    def lurk(self):  # Main method
        for el in self._root_webs:
            print("[{:s}]Starting url extraction on {:s}".format(self._name, el))
            uc = URLCrawler(el, self._maxDepth, self._lapse, self._headers, quiet=self._quiet)
            uc._domainBL = self._domainBL
            uc._domainWL = self._domainWL
            uc._extensionWL = self._extensionWL
            uc._extensionBL = self._extensionBL
            uc.crawlFrom(el)
            self._rawData[el] = uc.getRawData()
            print("[{:s}]Extracted content from {:d} urls on {:s}".format(self._name, uc._crawled, el))
        print("[{:s}]Starting the extraction".format(self._name))
        de = DataExtractor(self._rawData, self._fExtractors, self._rExtractors)
        de.extract()
        self._extractedData.update(de.getExtractedData())
        print("[{:s}]Extraction completed".format(self._name))
        print("[{:s}]Starting the refining".format(self._name))
        dr = DataRefiner(self._extractedData, self._refiners)
        dr.refine()
        self._refinedData.update(dr.getRefinedData())
        print("[{:s}]Refining completed".format(self._name))

    def addExtractor(self, extractor, name):
        if callable(extractor):
            self._addFExtractor(extractor, name)
        else:
            try:
                extractor.match("1")
            except AttributeError:
                raise Exception("Invalid Extractor: " + str(extractor))
            else:
                self._addRExtractor(extractor, name)

    def _addFExtractor(self, fextractor, name):
        self._fExtractors[name] = fextractor

    def _addRExtractor(self, rextractor, name):
        self._rExtractors[name] = rextractor

    def addRefiner(self, refiner):
        if callable(refiner):
            self._refiners.add(refiner)
        else:
            raise Exception("Invalid refiner: " + repr(refiner) + " is not a function")

    def getRawData(self, rootWeb=None):
        if rootWeb is not None and type(rootWeb) is str:
            try:
                return self._rawData[rootWeb]
            except:
                raise Exception(rootWeb + " does not exist")
        else:
            return self._rawData


    def getExtractedData(self):
        return self._extractedData

    def getRefinedData(self):
        if len(self._refinedData) == 0:
            return self._extractedData
        else:
            return self._refinedData

    def setMaxDepth(self, depth):
        self._maxDepth = depth

    def setLapse(self, lapse):
        self._lapse = lapse

    def getRootURLs(self):
        return self._root_webs

    def query(self, data, rootUrl=None, extractorId=None):
        if data == self.getRawData():
            raw = True
        elif data == self.getExtractedData() or data == self.getRefinedData():
            raw = False
        else:
            return None
        if rootUrl is None:
            return data
        else:
            if not raw:
                if extractorId is None:
                    return data[rootUrl]
                else:
                    return data[rootUrl][extractorId]
            else:
                return data[rootUrl]

    def blacklistDomain(self, domain):
        if type(domain) is str:
            domain = domain.replace("https://", "")
            domain = domain.replace("http://", "")
            self._domainBL.add(domain)
        elif type(domain) is set:
            for dom in domain:
                dom = dom.replace("https://", "")
                dom = dom.replace("http://", "")
                self._domainBL.add(dom)

    def whitelistDomain(self, domain):
        if type(domain) is str:
            domain = domain.replace("https://", "")
            domain = domain.replace("http://", "")
            self._domainWL.add(domain)
        elif type(domain) is set:
            for dom in domain:
                dom = dom.replace("https://", "")
                dom = dom.replace("http://", "")
                self._domainWL.add(dom)

    def getDomainBlackList(self):
        return self._domainBL

    def getDomainWhiteList(self):
        return self._domainWL

    def loadDirectory(self, pathToDirectory="./", recursive=False):
        self._rawData.update(FileManipulator(None, None).loadDirectory(pathToDirectory, recursive=recursive))

    def loadFile(self, filePath):
        self._rawData.update(FileManipulator(None, None).loadFile(filePath))

    def toJSON(self, filename=None):
        print("[{:s}]Saving as JSON...".format(self._name))
        fm = FileManipulator(self._extractedData, self._name)
        fm.jsonSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))

    def toPickle(self, filename=None):
        print("[{:s}]Saving as pickle...".format(self._name))
        fm = FileManipulator(self._extractedData, self._name)
        fm.pickleSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))

    def toText(self, filename=None):
        print("[{:s}]Saving as plain text...".format(self._name))
        fm = FileManipulator(self._extractedData, self._name)
        fm.textSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))


class URLCrawler():
    def __init__(self, rootURL, maxdepth, lapse, headers, quiet=False):
        self._rawData = set()
        self._rootURL = rootURL
        self._maxDepth = maxdepth
        self._lapse = lapse
        self._headers = headers
        self._quiet = quiet
        self._regexurl = re.compile('<a(?:.*?)href=\"(.*?)\"(?:.*?)</a>')
        self._maxDepth = maxdepth
        self._lapse = lapse
        self._crawled = 0
        self._rootURL = rootURL
        self._headers = headers
        self._quiet = quiet
        self._stickToDomain = True

        self._domainBL = set()
        self._extensionBL = set()
        self._domainWL = set()
        self._extensionWL = set()

        self._visitedURLs = set()
        self._rawData = set()

    def crawlFrom(self, webdir):
        self._extractURLData(webdir, 0)

    def getVisitedURLs(self):
        return self._visitedURLs

    def _extractURLData(self, webdir, depth):
        time.sleep(self._lapse)
        self._crawled += 1
        if not self._quiet:
            print("[{:s}]Gathering data from {:s} in depth {:d}".format(self._rootURL, webdir, depth))
        try:
            req = requests.get(webdir, verify=True, headers=self._headers)
        except:
            req = requests.get(webdir, verify=False, headers=self._headers)
        self._visitedURLs.add(webdir)
        self._rawData.add(req.text)
        urls = re.findall(self._regexurl, req.text)
        if depth < self._maxDepth:
            for url in urls:
                url = self._urlFilter(webdir, url)
                if url not in self._visitedURLs and url is not None:
                    self._visitedURLs.add(url)
                    self._extractURLData(url, depth + 1)


    def getRawData(self):
        return self._rawData

    def _urlFilter(self, web, url):  # TODO
        finalurl = str()
        tempurl = str()
        if url.startswith("https://") or url.startswith("http://"):
            finalurl = url
        else:
            if url.startswith("/"):
                finalurl = web[:len(web) - 1] + url
        if finalurl is None:
            return None
        tempurl = finalurl.replace("https://", "")
        tempurl = tempurl.replace("http://", "")
        isInDWList = False
        isInDBList = False
        isInEWList = False
        isInEBList = False

        if len(self._domainWL) > 0:
            for domain in self._domainWL:
                if tempurl.startswith(domain):
                    isInDWList = True
                    break
        if len(self._domainBL) > 0:
            for domain in self._domainBL:
                if tempurl.startswith(domain):
                    isInDBList = True
                    break
        if len(self._extensionWL) > 0:
            for extension in self._extensionWL:
                if tempurl.endswith(extension):
                    isInEWList = True
                    break
        if len(self._extensionBL) > 0:
            for extension in self._extensionBL:
                if tempurl.endswith(extension):
                    isInEBList = True
                    break
        if self._stickToDomain and not finalurl.startswith(web):
            return None
        if isInDBList or isInEBList:
            return None
        if len(self._domainWL) > 0 and not isInDWList:
            return None
        if len(self._extensionWL) > 0 and not isInEWList:
            return None
        return finalurl


class DataExtractor():
    def __init__(self, rawdata, fextractors, rextractors):
        self._rawData = rawdata  # ["root web": set datos html]
        self._fExtractors = fextractors
        self._rExtractors = rextractors
        self._extractedData = dict()  # ["root web": ["nombre extractor": set datos extraidos]]

    def extract(self):
        for rootWeb in self._rawData:
            self._extractedData[rootWeb] = self._extractF(rootWeb)
            self._extractedData[rootWeb].update(self._extractR(rootWeb))

    def getExtractedData(self):
        return self._extractedData


    def _extractF(self, rootWeb):
        extractedData = dict()
        for extractor in self._fExtractors:
            extractedSet = self._fExtractors[extractor](self._rawData[rootWeb])
            if type(extractedSet) is set:
                extractedData[extractor] = set()
                extractedData[extractor] |= extractedSet
            else:
                raise Exception("Extractor didn't return a set: " + extractor)

        return extractedData


    def _extractR(self, rootWeb):
        extractedData = dict()
        for extractor in self._rExtractors:
            extractedSet = set()
            for webdata in self._rawData[rootWeb]:
                for match in re.findall(self._rExtractors[extractor], webdata):
                    extractedSet.add(match)
            extractedData[extractor] = extractedSet
        return extractedData


class DataRefiner():
    def __init__(self, extractedData, refiners):
        self._extractedData = extractedData
        self._refiners = refiners
        self._refinedData = dict()

    def refine(self):
        for refiner in self._refiners:
            refiner(self._extractedData)

    def getRefinedData(self):
        return self._refinedData


class FileManipulator():
    def __init__(self, refinedData, filename):
        self._filename = filename
        self._refinedData = refinedData

    def loadFile(self, pathToFile):
        filecontent = set()
        fileDict = dict()
        if isfile(pathToFile) and (pathToFile.endswith(".html") or pathToFile.endswith(".htm")):
            with open(pathToFile, 'r') as f:
                filecontent.add(f.read())
            fileDict[pathToFile] = filecontent
        return fileDict

    def loadDirectory(self, pathToDirectory="./", recursive=False):
        directories = list()
        files = set()
        filesDict = dict()
        for f in listdir(pathToDirectory):
            if not f.startswith(".") and not f.startswith("_"):
                if isfile(join(pathToDirectory, f)):
                    if f.endswith(".html") or f.endswith(".htm"):
                        with open(pathToDirectory + f, 'r') as f:
                            files.add(f.read())
                else:
                    directories.append(f)
        if len(files) > 0:
            filesDict[pathToDirectory] = files

        for e in directories:
            if recursive:
                filesDict.update(self.loadDirectory(pathToDirectory + "/" + e + "/", recursive=recursive))
        return filesDict

    def jsonSave(self, filename=None):
        if filename is None:
            filename = self._filename
        if not filename.endswith(".json"):
            filename = filename + ".json"
        with open(filename, 'w') as file:
            jsonData = json.dumps(self._refinedData, cls=_SetEncoder)
            file.write(jsonData)

    def textSave(self, filename=None):
        if filename is None:
            filename = self._filename
        if not filename.endswith(".txt"):
            filename = filename + ".txt"
        with open(filename, 'w') as file:
            file.write(repr(self._refinedData))

    def pickleSave(self, filename=None):
        if filename is None:
            filename = self._filename
        if not filename.endswith(".pickle"):
            filename = filename + ".pickle"
        with open(filename, 'wb') as file:
            pickle.dump(self._refinedData, file, pickle.HIGHEST_PROTOCOL)


class _SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class HTMLTools():
    @staticmethod
    def html_to_text(html):
        parser = _HTMLToText()
        try:
            parser.feed(html)
            parser.close()
        except HTMLParseError:
            pass
        return parser.get_text()

    @staticmethod
    def text_to_html(text):
        def f(mo):
            t = mo.group()
            if len(t) == 1:
                return {'&': '&amp;', "'": '&#39;', '"': '&quot;', '<': '&lt;', '>': '&gt;'}.get(t)
            return '<a href="%s">%s</a>' % (t, t)

        return re.sub(r'https?://[^] ()"\';]+|[&\'"<>]', f, text)


class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))
