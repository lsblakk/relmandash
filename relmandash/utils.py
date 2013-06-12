from flask import session, render_template
from bugzilla.agents import BMOAgent
from dashboard.options import *
from dashboard.versions import *
from dashboard.utils import *
import urllib
import re


def initializeSession():
    if 'initialized' not in session.keys():
        session['initialized'] = True
        session['bmo'] = BMOAgent('', '')
        session['vt'] = VersionTracker()


def query_url_to_dict(url):
    if (';')in url:
        fields_and_values = url.split("?")[1].split(";")
    else:
        fields_and_values = url.split("?")[1].split("&")
    d = {}

    for pair in fields_and_values:
        (key, val) = pair.split("=")
        if key != "list_id":
            d[key] = urllib.unquote(val)
    return d


def getUserQueryBugs(query):
    buglist = []
    try:
        initializeSession()
        bmo = session['bmo']
        options = query_url_to_dict(query)
        try:
            buglist = bmo.get_bug_list(options)
            print buglist
        except:
            raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    except Exception, e:
        raise Exception("Failed to retrieve user query buglist: " + str(e))
    return buglist


def getProdCompBugs(product, components):
    buglist = []
    try:
        initializeSession()
        bmo = session['bmo']
        options = getProdComp(product, components, session['vt'])
        try:
            buglist = bmo.get_bug_list(options)
        except:
            raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    except Exception, e:
        raise Exception("Failed to retrieve product/component bugs: " + str(e))
    return buglist


def getAssignedBugs(emails):
    mainlist = []
    try:
        initializeSession()
        bmo = session['bmo']
        options = getAssignedOptions(emails, session['vt'])
        try:
            mainlist = bmo.get_bug_list(options)
        except:
            raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    except Exception, e:
        raise Exception("Failed to retrieve assigned bugs: " + str(e))
    return mainlist


def getToFollowBugs(emails):
    followlist = []
    try:
        initializeSession()
        bmo = session['bmo']
        followUpOptions = getToFollowUp(emails, session['vt'])
        try:
            followlist = bmo.get_bug_list(followUpOptions)
        except:
            raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    except Exception, e:
        raise Exception("Failed to retrieve landed bugs: " + str(e))
    return followlist
