from flask import Flask, request, session, redirect, url_for, render_template
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

def view_individual(email):
    error = ''
    mainlist=[]
    followlist=[]
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    try:
        if pattern.match(email):
            mainlist = getAssignedBugs(email)
            if email != 'nobody@mozilla.org':
                followlist = getToFollowBugs(email)
            print len(mainlist)
            print len(followlist)
        else:
            raise Exception('Invalid email address')
    except Exception, e:
        error = 'Individual view: ' + str(e)
    return render_template('individual.html', error=error, email=email, buglist=mainlist, followlist=followlist)

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
