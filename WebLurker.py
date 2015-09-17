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

        self._visitedURLs = dict()
        self._maxDepth = maxDepth
        self._lapse = lapse

        self._quiet = quiet
        self._name = name

        self._root_webs = list()

        self._fExtractors = dict()
        self._rExtractors = dict()
        self._cleanExtractorVals = dict()

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
        if type(urls) is list:
            self._root_webs = self._root_webs.union(urls)
        elif type(urls) is str:
            if urls not in self._root_webs:
                self._root_webs.append(urls)
        else:
            self._root_webs = self._root_webs + list(urls)

    def lurk(self):  # Main method
        for el in self._root_webs:  # TODO Multithreading
            print("[{:s}]Starting url extraction on {:s}".format(self._name, el))
            uc = URLCrawler(el, self._maxDepth, self._lapse, self._headers, quiet=self._quiet)
            uc._domainBL = self._domainBL
            uc._domainWL = self._domainWL
            uc._extensionWL = self._extensionWL
            uc._extensionBL = self._extensionBL
            uc.crawlFrom(el)
            self._rawData[el] = uc.getRawData()
            self._visitedURLs[el] = uc.getVisitedURLs()
            print("[{:s}]Extracted content from {:d} urls on {:s}".format(self._name, uc._crawled, el))
        print("[{:s}]Starting the extraction".format(self._name))
        de = DataExtractor(self._rawData, self._fExtractors, self._rExtractors, self._cleanExtractorVals)
        de.extract()
        self._extractedData.update(de.getExtractedData())
        print("[{:s}]Extraction completed".format(self._name))
        print("[{:s}]Starting the refining".format(self._name))
        dr = DataRefiner(self._extractedData, self._refiners)
        dr.refine()
        self._refinedData.update(dr.getRefinedData())
        print("[{:s}]Refining completed".format(self._name))

    def addExtractor(self, extractor, name, clean=False):
        if callable(extractor):
            self._addFExtractor(extractor, name)
            self._cleanExtractorVals[name] = clean
        else:
            try:
                extractor.match("1")
            except AttributeError:
                raise Exception("Invalid Extractor: " + str(extractor))
            else:
                self._addRExtractor(extractor, name)
                self._cleanExtractorVals[name] = clean

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

    def getVisitedURLs(self, rootURL=None):
        if rootURL is None or rootURL not in self._visitedURLs:
            return self._visitedURLs
        else:
            return self._visitedURLs[rootURL]

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

    def download(self, dir,filename=None):
        content = URLCrawler.fetch(dir)
        if filename is None:
            return content
        else:
            fm = FileManipulator(content, None)
            fm.fileSave(filename)

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

    def toFile(self, filename=None):
        print("[{:s}]Saving as plain text...".format(self._name))
        fm = FileManipulator(self._extractedData, self._name)
        fm.fileSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))


class URLCrawler():
    def __init__(self, rootURL, maxdepth, lapse, headers, quiet=False):
        self._rawData = list()
        self._rootURL = rootURL
        self._maxDepth = maxdepth
        self._lapse = lapse
        self._headers = headers
        self._quiet = quiet
        self._regexurl = re.compile('<a(?:.*?)href="(.*?)"(?:.*?)>')  # TODO Old one <a(?:.*?)href=\"(.*?)\"(?:.*?)</a>
        self._maxDepth = maxdepth
        self._lapse = lapse
        self._crawled = 0
        self._rootURL = rootURL
        self._headers = headers
        self._quiet = quiet
        self._continueOnDomain = True
        self._averageTime = self._lapse

        self._domainBL = set()
        self._extensionBL = set()
        self._domainWL = set()
        self._extensionWL = set()

        self._visitedURLs = set()

    def crawlFrom(self, webdir):
        self._extractURLData(webdir, 0)

    def getVisitedURLs(self):
        return self._visitedURLs

    def _extractURLData(self, webdir, depth):
        if self._lapse < self._averageTime or self._lapse == 0:
            time.sleep(self._lapse)
        else:
            print("Skipped lapse")
        self._crawled += 1
        if not self._quiet:
            print("[{:s}]Gathering data from {:s} in depth {:d}".format(self._rootURL, webdir, depth))
        try:
            stime = time.time()
            req = requests.get(webdir, verify=True, headers=self._headers)
            etime = time.time() - stime
        except:
            stime = time.time()
            req = requests.get(webdir, verify=False, headers=self._headers)
            etime = time.time() - stime
        self._averageTime = self._averageTime + (etime - self._averageTime) / self._crawled
        self._visitedURLs.add(webdir)
        self._rawData.append(req.text)
        urls = re.findall(self._regexurl, req.text)
        if depth < self._maxDepth:
            for url in urls:
                url = self._urlFilter(webdir, url)
                if url not in self._visitedURLs and url is not None:
                    self._visitedURLs.add(url)
                    self._extractURLData(url, depth + 1)

    @staticmethod
    def fetch(webdir):
        r = requests.get(webdir, verify=False)
        return r.content

    def getRawData(self):
        return self._rawData

    def _urlFilter(self, web, url):  # TODO
        finalurl = str()
        tempurl = str()

        if url.startswith("https://") or url.startswith("http://"):
            finalurl = url
        else:
            # finalurl = web[0:self.endOverlap(web, url)] + url
            finalurl = self._rootURL[0:self.endOverlap(web, url)] + url
        if finalurl is None:
            return None

        if self._continueOnDomain and not finalurl.startswith(web):
            return None

        return finalurl

    def endOverlap(self, a, b):
        for i in range(0, len(a)):
            if b.startswith(a[i:len(a) - 1]):
                return i
        return 0


class DataExtractor():
    def __init__(self, rawdata, fextractors, rextractors, cleanExtractorVals):
        self._rawData = rawdata  # ["root web": list datos html]
        self._fExtractors = fextractors
        self._rExtractors = rextractors
        self._extractedData = dict()  # ["root web": ["nombre extractor": list datos extraidos]]
        self._cleanExtractorVals = cleanExtractorVals

    def extract(self):
        for rootWeb in self._rawData:
            self._extractedData[rootWeb] = self._extractF(rootWeb)
            self._extractedData[rootWeb].update(self._extractR(rootWeb))

    def getExtractedData(self):
        return self._extractedData

    def _extractF(self, rootWeb):
        extractedData = dict()
        for extractor in self._fExtractors:
            if not self._cleanExtractorVals[extractor]:
                extractedList = self._fExtractors[extractor](self._rawData[rootWeb])
            else:
                extractedList = self._fExtractors[extractor](HTMLTools.html_to_text(self._rawData[rootWeb]))
            if type(extractedList) is list:
                extractedData[extractor] = list()
                extractedData[extractor] |= extractedList
            else:
                raise Exception("Extractor didn't return a list: " + extractor)

        return extractedData

    def _extractR(self, rootWeb):
        extractedData = dict()
        for extractor in self._rExtractors:
            extractedList = list()
            for webdata in self._rawData[rootWeb]:
                if not self._cleanExtractorVals[extractor]:
                    for match in re.findall(self._rExtractors[extractor], webdata):
                        extractedList.append(match)
                else:
                    for match in re.findall(self._rExtractors[extractor], HTMLTools.html_to_text(webdata)):
                        extractedList.append(match)
            extractedData[extractor] = extractedList
        return extractedData


class DataRefiner():
    def __init__(self, extractedData, refiners):
        self._extractedData = extractedData
        self._refiners = refiners
        self._refinedData = dict()

    def refine(self):
        for refiner in self._refiners:
            self._refinedData[refiner] = refiner(self._extractedData)

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

    def fileSave(self, filename=None):
        if filename is None:
            filename = self._filename
        if type(self._refinedData) is not bytes:
            with open(filename, 'w') as file:
                file.write(repr(self._refinedData))
        else:
            with open(filename, 'wb') as file:
                file.write(self._refinedData)

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
