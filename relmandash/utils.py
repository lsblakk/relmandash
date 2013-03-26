from flask import Flask, request, session
from bugzilla.agents import BMOAgent
from dashboard.options import *
from dashboard.versions import *
from dashboard.utils import *
import os
import hashlib

def initializeSession():
    if 'initialized' not in session.keys():
        session['initialized'] = True
        session['bmo'] = BMOAgent('','')
        session['vt'] = VersionTracker()

def verify_account(user, password):
    if user == None:
        raise Exception('Invalid Bugzilla email entered')
    m = hashlib.md5()
    m.update(user.salt.decode('base64'))
    m.update(password)
    _hash = m.digest()
    
    if _hash != user.hash.decode('base64'):
        raise Exception('Invalid password')
    return True
    
def getProdCompBugs(product, components):
    buglist = []
    try:
        initializeSession()
        bmo = session['bmo']
        options = getProdComp(product, components, session['vt'])
        buglist = bmo.get_bug_list(options)
    except Exception, e:
        raise Exception("Failed to retrieve product/component bugs: " + str(e))
    return buglist

def getAssignedBugs(emails):
    mainlist = []
    try:
        initializeSession()
        bmo = session['bmo']
        options = getAssignedOptions(emails)
        mainlist = bmo.get_bug_list(options)
    except Exception, e:
        raise Exception("Failed to retrieve assigned bugs: " + str(e))
    return mainlist

def getToFollowBugs(emails):
    followlist = []
    try:
        initializeSession()
        bmo = session['bmo']
        followUpOptions = getToFollowUp(emails, session['vt'])
        followlist = bmo.get_bug_list(followUpOptions)
    except Exception, e:
        raise Exception("Failed to retrieve landed bugs: " + str(e))
    return followlist
