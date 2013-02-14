from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack, jsonify
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
import re
from dashboard.options import *
from dashboard.versions import *
from dashboard.products import *
from utils import *

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()
        
@app.route('/')
def index():
    session['logged_in'] = False
    return render_template('index.html')

@app.route('/newaccount', methods=['POST'])
def login():
    error = None
    try:
        username = request.form['email']
        password = request.form['password']
        bmo = BMOAgent(session['username'], session['password'])
        bug = bmo.get_bug('80000');
        session['logged_in'] = True
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        error = 'Invalid username or password'
    return redirect(url_for('view_individual', email="liannelee719@hotmail.com"))
    
@app.route('/login', methods=['POST'])
def login():
    error = None
    try:
        session['username'] = request.form['email']
        session['password'] = request.form['password']
        bmo = session['bmo'] = BMOAgent(session['username'], session['password'])
        bug = bmo.get_bug('80000');
        session['logged_in'] = True
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        session['bmo'] = None
        error = 'Invalid username or password'
    return redirect(url_for('view_individual', email="liannelee719@hotmail.com"))

"""
    INDIVIDUAL ROUTING
"""
@app.route('/email/<string:email>')
def view_individual(email):
    error = 'Invalid email address'
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    if pattern.match(email):
        try:
            bmo = session['bmo'] = BMOAgent(session['username'], session['password'])
        except:
            bmo = session['bmo'] = BMOAgent('','')
        try:
            session['email'] = email
            options = getAssignedOptions(email)
            buglist = bmo.get_bug_list(options)
            keywords = getKeywords(buglist)
            session['vt'] = vt = VersionTracker()
            
            beta = getTrackedBugs(vt.beta, buglist)
            aurora = getTrackedBugs(vt.aurora, buglist)
            esr = getTrackedBugs(vt.esr, buglist)
            
            needsInfoOptions = getNeedsInfo(email)
            needsInfo = bmo.get_bug_list(needsInfoOptions)
            
            followUpOptions = getToFollowUp(email, vt.beta, vt.aurora)
            buglist = bmo.get_bug_list(followUpOptions)
            print len(buglist)
            for bug in buglist:
                print bug.id
            toNominate = getToNominateBugs(vt.beta, vt.aurora, buglist)
            toApprove = getToApproveBugs(buglist)
            toUplift = getToUpliftBugs(vt.beta, vt.aurora, buglist)
            
            return render_template('individual.html', email=email, beta=beta, aurora=aurora, esr=esr, needsInfo=needsInfo, nominate=toNominate, approve=toApprove, uplift=toUplift)
        except ServerError, e:
            error = 'Error requesting bugs from server. Details: \n'+e
        except Exception, e:
            error = e
    return render_template('individual.html', error=error)
    
@app.route('/info')
def needs_info():
    needsInfoJSON = []
    try:
        bmo = session['bmo']
        needsInfoOptions = getNeedsInfo(session['email'])
        needsInfo = bmo.get_bug_list(needsInfoOptions)
        for bug in needsInfo:
            needsInfoJSON.append(bug.jsonify())
    except:
        print 'error in /info'
    return jsonify(result=needsInfoJSON)

@app.route('/nominate')
def nominate():
    print 'nominate'
    toNominateJSON = []
    try:
        vt = session['vt']
        bmo = session['bmo']
        followUpOptions = getToFollowUp(session['email'], vt.beta, vt.aurora)
        buglist = session['followUpList'] = bmo.get_bug_list(followUpOptions)
        print len(buglist)
        toNominate = getToNominateBugs(vt.beta, vt.aurora, buglist)
        for bug in toNominate:
            toNominateJSON.append(bug.jsonify())
    except:
        print 'error in /nominate'
    return jsonify(result=toNominateJSON)
    
@app.route('/approve')
def approve():
    toApproveJSON = []
    try:
        vt = session['vt']
        bmo = session['bmo']
        followUpOptions = getToFollowUp(session['email'], vt.beta, vt.aurora)
        buglist = session['followUpList']
        print len(buglist)
        toApprove = getToApproveBugs(buglist)
        for bug in toApprove:
            toApproveJSON.append(bug.jsonify())
    except:
        print 'error in /approve'
    return jsonify(result=toApproveJSON)
    
@app.route('/uplift')
def uplift():
    toUpliftJSON = []
    try:
        vt = session['vt']
        bmo = session['bmo']
        followUpOptions = getToFollowUp(session['email'], vt.beta, vt.aurora)
        buglist = session['followUpList']
        print len(buglist)
        toUplift = getToUpliftBugs(vt.beta, vt.aurora, buglist)
        for bug in toUplift:
            toUpliftJSON.append(bug.jsonify())
    except:
        print 'error in /uplift'
    return jsonify(result=toUpliftJSON)

"""
    PRODUCT/COMPONENT ROUTING
"""
@app.route('/<string:product>')
@app.route('/<string:product>/<string:component>')
def view_prodcomp(product, component=''):
    error = 'Invalid product or component'
    ct = ComponentsTracker()
    vt = VersionTracker()
    try:
        if product in ct.products:
            print product
            p = ct.products[product]
            if component in p.component or component == '':
                bmo = initializeSession()
                buglist = bmo.get_bug_list(getProdComp(product, component, vt.beta, vt.aurora, vt.esr))
                
                if len(buglist) > 0:
                    beta = getTrackedBugs(vt.beta, buglist)
                    aurora = getTrackedBugs(vt.aurora, buglist)
                    esr = getTrackedBugs(vt.esr, buglist)
                    unassigned = getUnassignedBugs(buglist)
                    info = getNeedsInfoBugs(buglist)
                    keywords = getKeywords(buglist)
                    
                    return render_template('prodcomp.html', beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info, keywords=keywords)
                else:
                    error = 'Looks like there are no tracked bugs for this product/component!'
    except ServerError, e:
        error = 'Error requesting bugs from server. Details: \n'+e
    except Exception, e:
        error = e
    return render_template('prodcomp.html', error=error)     

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are now logged out')
    return redirect(url_for('view_individual'))

def initializeSession():
    try:
        bmo = session['bmo']
    except:
        bmo = session['bmo'] = BMOAgent('','')
    return bmo

if __name__ == '__main__':
    app.run()
