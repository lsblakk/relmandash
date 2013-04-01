import urllib2
import re
import datetime
import subprocess
import os
import json
from argparse import ArgumentParser

def getTemplateValue(url):
    version_regex = re.compile(".*<p>(.*)</p>.*")
    template_page = urllib2.urlopen(url).read().replace('\n', '')
    parsed_template = version_regex.match(template_page)
    return parsed_template.groups()[0]
