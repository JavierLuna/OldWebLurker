import re
import time
import json
import pickle
from os import listdir
from os.path import isfile, join
from HTMLParser import HTMLParser, HTMLParseError

import requests

__author__ = 'jluna'

name2codepoint = {'Omicron': 927, 'crarr': 8629, 'nsub': 8836, 'Ocirc': 212, 'thetasym': 977, 'aelig': 230, 'beta': 946, 'Psi': 936, 'sect': 167, 'lrm': 8206, 'ordm': 186, 'uarr': 8593, 'Uacute': 218, 'Atilde': 195, 'emsp': 8195, 'acirc': 226, 'uml': 168, 'Oacute': 211, 'middot': 183, 'tilde': 732, 'eta': 951, 'egrave': 232, 'ni': 8715, 'uArr': 8657, 'quot': 34, 'raquo': 187, 'Alpha': 913, 'alpha': 945, 'macr': 175, 'Eta': 919, 'hArr': 8660, 'Sigma': 931, 'iuml': 239, 'Chi': 935, 'Euml': 203, 'OElig': 338, 'reg': 174, 'curren': 164, 'ograve': 242, 'Icirc': 206, 'lambda': 955, 'mdash': 8212, 'part': 8706, 'Beta': 914, 'sube': 8838, 'rceil': 8969, 'rang': 9002, 'Iuml': 207, 'sbquo': 8218, 'ocirc': 244, 'Aacute': 193, 'equiv': 8801, 'Eacute': 201, 'uuml': 252, 'zeta': 950, 'ouml': 246, 'hellip': 8230, 'Pi': 928, 'sigmaf': 962, 'Nu': 925, 'iexcl': 161, 'sub': 8834, 'frac14': 188, 'Kappa': 922, 'eth': 240, 'sup1': 185, 'supe': 8839, 'upsilon': 965, 'Ugrave': 217, 'Scaron': 352, 'plusmn': 177, 'rsaquo': 8250, 'scaron': 353, 'diams': 9830, 'Gamma': 915, 'and': 8743, 'Epsilon': 917, 'igrave': 236, 'oplus': 8853, 'sdot': 8901, 'lfloor': 8970, 'Egrave': 200, 'aacute': 225, 'sup2': 178, 'acute': 180, 'weierp': 8472, 'Igrave': 204, 'nbsp': 160, 'iacute': 237, 'infin': 8734, 'real': 8476, 'ldquo': 8220, 'bdquo': 8222, 'alefsym': 8501, 'upsih': 978, 'prod': 8719, 'cap': 8745, 'Phi': 934, 'otilde': 245, 'sim': 8764, 'Acirc': 194, 'cup': 8746, 'yacute': 253, 'Rho': 929, 'fnof': 402, 'darr': 8595, 'dagger': 8224, 'lsaquo': 8249, 'piv': 982, 'lsquo': 8216, 'lArr': 8656, 'there4': 8756, 'Agrave': 192, 'agrave': 224, 'zwnj': 8204, 'deg': 176, 'spades': 9824, 'hearts': 9829, 'iota': 953, 'euro': 8364, 'isin': 8712, 'rdquo': 8221, 'ndash': 8211, 'rArr': 8658, 'oacute': 243, 'Iacute': 205, 'not': 172, 'Tau': 932, 'Iota': 921, 'rlm': 8207, 'or': 8744, 'copy': 169, 'uacute': 250, 'oslash': 248, 'asymp': 8776, 'lceil': 8968, 'oline': 8254, 'Otilde': 213, 'Upsilon': 933, 'lt': 60, 'xi': 958, 'auml': 228, 'ang': 8736, 'phi': 966, 'Aring': 197, 'Ecirc': 202, 'ccedil': 231, 'eacute': 233, 'bull': 8226, 'ge': 8805, 'ordf': 170, 'pound': 163, 'image': 8465, 'Uuml': 220, 'atilde': 227, 'prop': 8733, 'exist': 8707, 'laquo': 171, 'cong': 8773, 'ntilde': 241, 'thorn': 254, 'Ccedil': 199, 'Dagger': 8225, 'cedil': 184, 'frac34': 190, 'tau': 964, 'epsilon': 949, 'empty': 8709, 'iquest': 191, 'frac12': 189, 'circ': 710, 'sup': 8835, 'yen': 165, 'lowast': 8727, 'theta': 952, 'ugrave': 249, 'Omega': 937, 'Zeta': 918, 'para': 182, 'ne': 8800, 'pi': 960, 'rarr': 8594, 'ETH': 208, 'lang': 9001, 'sup3': 179, 'AElig': 198, 'forall': 8704, 'rho': 961, 'nabla': 8711, 'thinsp': 8201, 'rsquo': 8217, 'permil': 8240, 'Theta': 920, 'ensp': 8194, 'larr': 8592, 'nu': 957, 'Prime': 8243, 'dArr': 8659, 'szlig': 223, 'cent': 162, 'gamma': 947, 'Ucirc': 219, 'omega': 969, 'Ntilde': 209, 'divide': 247, 'int': 8747, 'brvbar': 166, 'Oslash': 216, 'Lambda': 923, 'otimes': 8855, 'Ograve': 210, 'shy': 173, 'sum': 8721, 'Auml': 196, 'harr': 8596, 'perp': 8869, 'loz': 9674, 'omicron': 959, 'zwj': 8205, 'Yuml': 376, 'rfloor': 8971, 'psi': 968, 'Mu': 924, 'THORN': 222, 'micro': 181, 'ucirc': 251, 'aring': 229, 'ecirc': 234, 'prime': 8242, 'le': 8804, 'yuml': 255, 'chi': 967, 'frasl': 8260, 'radic': 8730, 'mu': 956, 'amp': 38, 'minus': 8722, 'sigma': 963, 'trade': 8482, 'kappa': 954, 'icirc': 238, 'oelig': 339, 'times': 215, 'gt': 62, 'euml': 235, 'Delta': 916, 'Yacute': 221, 'Xi': 926, 'Ouml': 214, 'notin': 8713, 'delta': 948, 'clubs': 9827}


class WebLurker:
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
            uc = URLCrawler(maxdepth=self._maxDepth, lapse=self._lapse, headers=self._headers, quiet=self._quiet)
            uc.crawlFrom(el)
            self._rawData[el] = uc.getRawData()
            self._visitedURLs[el] = uc.getVisitedURLs()
            print("[{:s}]Extracted content from {:d} urls on {:s}".format(self._name, uc._crawled, el))
        print("[{:s}]Starting the extraction".format(self._name))
        de = DataExtractor(self._rawData, fextractors=self._fExtractors, rextractors=self._rExtractors, cleanExtractorVals=self._cleanExtractorVals)
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
        if rootWeb and type(rootWeb) is str:
            try:
                return self._rawData[rootWeb]
            except:
                raise Exception(rootWeb + " does not exist")
        else:
            return self._rawData

    def getVisitedURLs(self, rootURL=None):
        if rootURL or rootURL not in self._visitedURLs:
            return self._visitedURLs
        else:
            return self._visitedURLs[rootURL]

    def getExtractedData(self):
        return self._extractedData

    def getRefinedData(self):
        if self._refinedData:
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
        if filename:
            fm = FileManipulator(content, None)
            fm.fileSave(filename)
        return content

    def query(self, data, rootUrl=None, extractorId=None):
        if data == self.getRawData():
            raw = True
        elif data == self.getExtractedData() or data == self.getRefinedData():
            raw = False
        else:
            return None
        if not rootUrl:
            return data
        else:
            if not raw:
                if not extractorId:
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
        self._rawData.update(FileManipulator().loadDirectory(pathToDirectory, recursive=recursive))

    def loadFile(self, filePath):
        self._rawData.update(FileManipulator().loadFile(filePath))

    def toJSON(self, filename=None):
        print("[{:s}]Saving as JSON...".format(self._name))
        fm = FileManipulator(refinedData=self._extractedData, filename=self._name)
        fm.jsonSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))

    def toPickle(self, filename=None):
        print("[{:s}]Saving as pickle...".format(self._name))
        fm = FileManipulator(refinedData=self._extractedData, filename=self._name)
        fm.pickleSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))

    def toFile(self, filename=None):
        print("[{:s}]Saving as plain text...".format(self._name))
        fm = FileManipulator(refinedData=self._extractedData, filename=self._name)
        fm.fileSave(filename=filename)
        print("[{:s}]Saving completed".format(self._name))


class URLCrawler:
    def __init__(self, maxdepth=0, lapse=0, headers={'User-Agent': 'Mozilla/5.0'}, quiet=False):
        self._rawData = list()
        self._regexurl = re.compile('<a(?:.*?)href="(.*?)"(?:.*?)>')  # TODO Old one <a(?:.*?)href=\"(.*?)\"(?:.*?)</a>
        self._maxDepth = maxdepth
        self._lapse = lapse
        self._crawled = 0
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
        self._rootURL = webdir
        self._extractURLData(webdir, 0)

    def _extractURLData(self, webdir, depth):
        if self._lapse < self._averageTime or not self._lapse:
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
                if url not in self._visitedURLs and url:
                    self._visitedURLs.add(url)
                    self._extractURLData(url, depth + 1)

    @staticmethod
    def fetch(webdir):
        r = requests.get(webdir, verify=False)
        return r.content

    def setMaxDepth(self, depth):
        self._maxDepth = depth

    def setURLRegex(self, regex):
        try:
            regex.match("1")
        except AttributeError:
            raise Exception(repr(regex)+" is not a regular expression")
        else:
            self._regexurl = regex

    def setLapse(self, lapse):
        self._lapse = lapse

    def setHeaders(self, headers):
        self._headers = headers

    def setQuiet(self, quiet):
        self._quiet = quiet

    def setContinueOnDomain(self, continueOnDomain):
        self._continueOnDomain = continueOnDomain

    def getRawData(self):
        return self._rawData

    def getVisitedURLs(self):
        return self._visitedURLs

    def getMaxDepth(self):
        return self._maxDepth

    def getURLRegex(self):
        return self._regexurl

    def getLapse(self):
        return self._lapse

    def getHeaders(self):
        return self._headers

    def getQuiet(self):
        return self._quiet

    def getcontinueOnDomain(self):
        return self._continueOnDomain

    def _urlFilter(self, web, url):  # TODO
        finalurl = str()
        tempurl = str()

        if url.startswith("https://") or url.startswith("http://"):
            finalurl = url
        else:
            # finalurl = web[0:self.endOverlap(web, url)] + url
            finalurl = self._rootURL[0:self._endOverlap(web, url)] + url
        if not finalurl:
            return None

        if self._continueOnDomain and not finalurl.startswith(web):
            return None

        return finalurl

    @staticmethod
    def _endOverlap(a, b):
        for i in range(0, len(a)):
            if b.startswith(a[i:len(a) - 1]):
                return i
        return 0


class DataExtractor:
    def __init__(self, rawdata, fextractors=dict(), rextractors=dict(), cleanExtractorVals=dict()):
        self._rawData = rawdata  # ["root web": list datos html]
        self._fExtractors = fextractors
        self._rExtractors = rextractors
        self._extractedData = dict()  # ["root web": ["nombre extractor": list datos extraidos]]
        self._cleanExtractorVals = cleanExtractorVals

    def extract(self):
        for rootWeb in self._rawData:
            self._extractedData[rootWeb] = self._extractF(rootWeb)
            self._extractedData[rootWeb].update(self._extractR(rootWeb))

    def setRawData(self, rawdata):
        self._rawData = rawdata

    def setFunctionExtractors(self, fextractors, cleanValues):
        self._fExtractors = fextractors
        self._cleanExtractorVals.update(cleanValues)

    def setRegexExtractors(self, rextractors, cleanValues):
        self._rExtractors = rextractors
        self._cleanExtractorVals.update(cleanValues)

    def updateCleanValues(self, cleanValues):
        self._cleanExtractorVals.update(cleanValues)

    def getRawData(self):
        return self._rawData

    def getExtractedData(self):
        return self._extractedData

    def getFExtractors(self):
        return self._fExtractors

    def getRExtractors(self):
        return self._rExtractors

    def getCleanValues(self):
        return self._cleanExtractorVals

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


class DataRefiner:
    def __init__(self, extractedData, refiners):
        self._extractedData = extractedData
        self._refiners = refiners
        self._refinedData = dict()

    def refine(self):
        for refiner in self._refiners:
            self._refinedData[refiner] = refiner(self._extractedData)

    def getRefinedData(self):
        return self._refinedData


class FileManipulator:
    def __init__(self, refinedData=None, filename="NoName"):
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

    def jsonSave(self,filename, data=None):
        if not filename :
            filename = self._filename
        if not data:
            data = self._refinedData
        if not filename.endswith(".json"):
            filename = filename + ".json"
        with open(filename, 'w') as file:
            jsonData = json.dumps(data, cls=_SetEncoder)
            file.write(jsonData)

    def fileSave(self, filename, data=None):
        if not filename:
            filename = self._filename
        if not data:
            data = self._refinedData
        if type(data) is not bytes:
            with open(filename, 'w') as file:
                file.write(repr(data))
        else:
            with open(filename, 'wb') as file:
                file.write(data)

    def pickleSave(self, filename, data=None):
        if not filename:
            filename = self._filename
        if not data:
            data = self._refinedData
        if not filename.endswith(".pickle"):
            filename = filename + ".pickle"
        with open(filename, 'wb') as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)


class _SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class HTMLTools:
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
