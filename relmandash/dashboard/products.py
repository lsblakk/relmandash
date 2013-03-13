import yaml
from urllib2 import Request, urlopen, URLError
from relmandash.models import Product, Component

class ComponentsTracker:
    def __init__(self, db):
        req = Request('https://api-dev.bugzilla.mozilla.org/latest/configuration')
        try:
            response = urlopen(req)
            document = response.read()
            yamlDoc = yaml.load(document)
            yamlProducts = yamlDoc['product']
            for prodname in yamlProducts.keys():
                product = yamlProducts[prodname]
                p = Product(int(product['id']), prodname)
                db.session.add(p)
                components = product['component']
                for compname in components.keys():
                    component = components[compname]
                    c = Component(component['id'], compname, p)
                    db.session.add(c)
            db.session.commit()
        except URLError, e:
            print e
