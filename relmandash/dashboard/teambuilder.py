from HTMLParser import HTMLParser
from urllib2 import Request, urlopen, URLError
import re
import exceptions

raw_data = []
products_components = {}


class TeamParser(HTMLParser):

    def handle_data(self, data):
        raw_data.append(data)

    def print_data(self):
        for data in raw_data:
            if data.strip():
                print data


req = Request('https://wiki.mozilla.org/Modules/All')
try:
    response = urlopen(req)
    parser = TeamParser()
    html = response.read()
    parser.feed(html)
    #parser.print_data()
    i = 0
    product_count = 1
    product_encountered = False
    component_encountered = False

    for line in raw_data:
        if line.strip():
            if product_encountered:
                products_components[line] = []
                product_count = product_count + 1
                product_encountered = False
            elif component_encountered:
                split = re.split('::|, ', line)
                for j in range(len(split)):
                    if j % 2:
                        try:
                            products_components[split[j-1]].append(split[j])
                        except exceptions.KeyError:
                            products_components[split[j-1]] = [split[j]]
                component_encountered = False
            # TODO(lsblakk): Get list of main modules as products
            try:
                if int(line) == product_count:
                    product_encountered = True
            except exceptions.ValueError:
                if line == 'Bugzilla Component(s):':
                    component_encountered = True

    for k, v in products_components.iteritems():
        print k, ": ", v

except URLError, e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
