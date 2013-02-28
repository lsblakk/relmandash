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
app.config['PROPAGATE_EXCEPTIONS'] = True

def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
current application context.
"""
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return top.sqlite_db

@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()
        
@app.route('/')
def index():
    if 'logged_in' not in session.keys():
        session['logged_in'] = False
    session['last_url'] = 'index'
    message = ''
    email = request.args.get('email')
    product = request.args.get('product')
    component = request.args.get('component')
    style = request.args.get('style')
    if email:
        return view_individual(email)
    elif product:
        return view_prodcomp(product=product, component=component, style=style)
    elif request.args.keys():
        error = 'Invalid query entered!'
        return render_template('index.html', error=error)
    return render_template('index.html', message=message)

@app.route('/newaccount', methods=['POST'])
def login():
    error = None
    try:
        username = request.form['email']
        password = request.form['password']
        
        # verify email and password
        bmo = BMOAgent(session['username'], session['password'])
        bug = bmo.get_bug('80000')
        
        db = get_db()
        db.execute('insert into users (email, password) values (?, ?)',
                     username, password)
        db.commit()
        return redirect(url_for('index'))
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        error = 'Invalid username or password'
    return render_template('index.html', message=message)
    
@app.route('/login', methods=['POST'])
def login():
    error = None
    try:
        session['username'] = request.form['email']
        session['password'] = request.form['password']
        bmo = session['bmo'] = BMOAgent(session['username'], session['password'])
        bug = bmo.get_bug('80000')
        session['logged_in'] = True
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        session['bmo'] = None
        error = 'Invalid username or password'
    return redirect(url_for('index'))
    
"""
    INDIVIDUAL ROUTING
"""
@app.route('/email/<string:email>')
def view_individual(email):
    error = ''
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
            keywords = getKeywords(buglist)
        except AttributeError, e:
            print 'View Individual: ' + str(e)
            error = e
        except Exception, e:
            error = e
    else:
        error = 'Invalid email address'
    return render_template('individual.html', error=error, email=email, beta=beta, aurora=aurora, esr=esr, info=needsInfo, nominate=toNominate, approve=toApprove, uplift=toUplift, keywords=keywords)

"""
    PRODUCT/COMPONENT ROUTING
"""
@app.route('/<string:product>')
@app.route('/<string:product>/')
@app.route('/<string:product>/<string:component>')
def view_prodcomp(product, component='', style=''):
    error = 'Invalid product or component'
    ct = ComponentsTracker()
    vt = VersionTracker()
    if component is None:
        component = ''
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
                    components = getComponents(buglist)
                    if style == 'table':
                        return render_template('prodcomptable.html', product=product, component=component, beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info, keywords=keywords)
                    elif style == 'count':
                        return render_template('prodcompcount.html', product=product, component=component, beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info, components=components)
                    else:
                        return render_template('prodcomplist.html', product=product, component=component, beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info, keywords=keywords, components=components)
                else:
                    error = 'Looks like there are no tracked bugs for this product/component!'
    except Exception, e:
        error = e
    return render_template('prodcomplist.html', error=error)     

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('password', None)
    message = 'You are now logged out'
    return redirect(url_for('index'), message=message)

def initializeSession():
    try:
        bmo = session['bmo']
    except:
        bmo = session['bmo'] = BMOAgent('','')
    return bmo

if __name__ == '__main__':
    app.run()
