from report import getTemplateValue

class VersionTracker:
    beta = ''
    aurora = ''
    central = ''
    next = ''
    esr = '_esr'
    shipdate = ''
    cycle = ''
    baseurl = "https://wiki.mozilla.org/Template:"
    version_map = {}
    
    def __init__(self):
        self.beta = getTemplateValue(self.baseurl + 'BETA_VERSION')
        self.version_map['{{BETA_VERSION}}'] = self.beta
        self.aurora = getTemplateValue(self.baseurl + 'AURORA_VERSION')
        self.version_map['{{AURORA_VERSION}}'] = self.aurora
        self.esr = self.esr + getTemplateValue(self.baseurl + 'ESR_VERSION')
        self.version_map['{{ESR_VERSION}}'] = self.esr
        self.central = getTemplateValue(self.baseurl + 'CENTRAL_VERSION')
        self.version_map['{{CENTRAL_VERSION}}'] = self.central
        self.next = getTemplateValue(self.baseurl + 'NEXT_VERSION')
        self.version_map['{{NEXT_VERSION}}'] = self.next
        self.shipdate = getTemplateValue(self.baseurl + 'FIREFOX_SHIP_DATE')
        self.version_map['{{FIREFOX_SHIP_DATE}}'] = self.shipdate
        self.cycle = getTemplateValue(self.baseurl + 'CURRENT_CYCLE')
        self.version_map['{{CURRENT_CYCLE}}'] = self.cycle

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)