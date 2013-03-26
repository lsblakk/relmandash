from report import getTemplateValue

class VersionTracker:
    beta = ''
    aurora = ''
    central = ''
    esr = '_esr'
    cycle = ''
    baseurl = "https://wiki.mozilla.org/Template:"
    
    def __init__(self):
        self.beta = getTemplateValue(self.baseurl + 'BETA_VERSION')
        self.aurora = getTemplateValue(self.baseurl + 'AURORA_VERSION')
        self.esr = self.esr + getTemplateValue(self.baseurl + 'ESR_VERSION')
        self.central = getTemplateValue(self.baseurl + 'CENTRAL_VERSION')
        self.cycle = getTemplateValue(self.baseurl + 'CURRENT_CYCLE')
