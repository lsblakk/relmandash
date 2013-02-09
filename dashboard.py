from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
import re
from dashboard.options import *
from dashboard.versions import *
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
        bmo = BMOAgent(session['username'], session['password'])
        bug = bmo.get_bug('80000');
        session['logged_in'] = True
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
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
            bmo = BMOAgent(session['username'], session['password'])
        except:
            bmo = BMOAgent('','')
            
        options = getAssignedOptions(email)
        buglist = bmo.get_bug_list(options)
        keywords = getKeywords(buglist)
        vt = VersionTracker()
        
        security = getSecurityBugs(buglist)
        beta = getTrackedBugs(vt.beta, buglist)
        aurora = getTrackedBugs(vt.aurora, buglist)
        esr = getTrackedBugs(vt.esr, buglist)
        
        followUpOptions = getToFollowUp(email, vt.beta, vt.aurora)
        buglist = bmo.get_bug_list(followUpOptions)
        keywords = getKeywords(buglist)

        toApprove = getToApproveBugs(buglist)
        toNominate = getToNominateBugs(vt.beta, vt.aurora, buglist)
        toUplift = getToUpliftBugs(vt.beta, vt.aurora, buglist)
        
        needsInfoOptions = getNeedsInfo(email)
        needsInfo = bmo.get_bug_list(needsInfoOptions)
        
        return render_template('individual.html', email=email, beta=beta, aurora=aurora, esr=esr, security=security, nominate=toNominate, approve=toApprove, uplift=toUplift, needsInfo=needsInfo, keywords=keywords)
    return render_template('individual.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are now logged out')
    return redirect(url_for('view_individual'))


if __name__ == '__main__':
    app.run()
