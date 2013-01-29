from HTMLParser import HTMLParser
from urllib2 import Request, urlopen, URLError
import re
import exceptions

class VersionParser(HTMLParser):
    p_encountered = False
    version = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.p_encountered = True
        else:
            self.p_encountered = False
        
    def handle_data(self, data):
        if self.p_encountered:
            try:
                self.version = int(data)
            except exceptions.ValueError:
                pass


class VersionTracker:
    beta = 0
    aurora = 0
    central = 0
    esr = '_esr17'
    baseurl = "https://wiki.mozilla.org/Template:"
    
    def __init__(self):
        url = self.baseurl + 'BETA_VERSION'
        self.beta = self.parseVersion(url)
        
        url = self.baseurl + 'AURORA_VERSION'
        self.aurora = self.parseVersion(url)
        
        url = self.baseurl + 'CENTRAL_VERSION'
        self.central = self.parseVersion(url)
        
                
    def parseVersion(self, url):
        req = Request(url)
        try:
            response = urlopen(req)
            parser = VersionParser()
            parser.feed(response.read())
            return parser.version
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
        return 0
        
