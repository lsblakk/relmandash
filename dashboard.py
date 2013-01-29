from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
import re
from dashboard.options import *
from dashboard.versions import *

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
    return render_template('index.html')

"""
    INDIVIDUAL ROUTING
"""

@app.route('/email/<string:email>', methods=['GET', 'POST'])
def view_individual(email):
    error = 'Invalid email address'
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    if pattern.match(email):
        username, password = get_credentials()
        bmo = BMOAgent(username, password)
        options = getAssignedOptions(email)
        buglist = bmo.get_bug_list(options)
        vt = VersionTracker()
        
        beta = getTrackedBugs(vt.beta, buglist)
        aurora = getTrackedBugs(vt.aurora, buglist)
        esr = getTrackedBugs(vt.esr, buglist)
        security = getSecurityBugs(buglist)
        
        return render_template('individual.html', beta=beta, aurora=aurora, esr=esr, security=security)
    return render_template('individual.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are now logged out')
    return redirect(url_for('view_individual'))


if __name__ == '__main__':
    app.run()
