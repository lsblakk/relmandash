import yaml
from urllib2 import Request, urlopen, URLError
from bugzilla.models import Component

class Product():
    id = 0
    description = ''
    is_active = False
    is_permitting_unconfirmed = False
    classification = ''
    component = {}
    version = []
    target_milestone = []
    default_target_milestone = ''
    group = []
    
    def __repr__(self):
        return '<Product %s: "%s">' % (self.id, self.description)

    def __str__(self):
        return "[Product %s] - %s" % (self.id, self.description)

    def __hash__(self):
        return self.id

class ComponentsTracker:
    products = {}
    
    def __init__(self):
        req = Request('https://api-dev.bugzilla.mozilla.org/latest/configuration')
        try:
            response = urlopen(req)
            document = response.read()
            yamlDoc = yaml.load(document)
            yamlProducts = yamlDoc['product']
            for prodname in yamlProducts.keys():
                product = yamlProducts[prodname]
                p = Product()
                p.id = product['id']
                p.description = product['description']
                p.is_active = product['is_active']
                p.is_permitting_unconfirmed = product['is_permitting_unconfirmed']
                p.classification = product['classification']
                p.version = product['version']
                p.target_milestone = product['target_milestone']
                p.default_target_milestone = product['default_target_milestone']
                p.group = product['group']
                p.component = {}
                components = product['component']
                for compname in components.keys():
                    component = components[compname]
                    c = Component()
                    c.id = component['id']
                    c.description = component['description']
                    c.flag_type = component['flag_type']
                    p.component[compname] = c
                self.products[prodname] = p
            
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
