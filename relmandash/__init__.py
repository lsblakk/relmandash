from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
import re
from dashboard.options import *
from dashboard.versions import *
from dashboard.products import *
from utils import *
import os
import hashlib

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

db_conn = 'postgresql://localhost/dashboard' 
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn
db = SQLAlchemy(app)

def init_db():
    """Creates the database tables."""
    db.create_all()

@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
        
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
        print 'weird query'
        error = 'Invalid query entered!'
        return render_template('index.html', error=error)
    '''else:
        user = User.query.all()
        if len(user) == 0:
            return 'no entries'
    '''
    return render_template('index.html', message=message)
    
def clever_function():
    bmo = BMOAgent('liannelee719@hotmail.com', 'Le3Ch0o!Tz3')
    bug = bmo.get_bug('80000')
    return bug
    
app.jinja_env.globals.update(clever_function=clever_function)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    try:
        if request.method == 'GET':
            return render_template('signup.html')
        else:
            email = request.form['email']
            password = request.form['password']
            view = request.form['view']
            
            if password != request.form['confirmpassword']:
                error = 'Please re-enter the same password'
                print error
            
            if error != None:
                # verify email and password
                bmo = BMOAgent(email, password)
                bug = bmo.get_bug('80000')
            
                #generate salt
                salt = os.urandom(16)
                
                m = hashlib.md5()
                m.update(salt)
                m.update(password)
                _hash = m.digest()
                
                user = User(email=email, _hash=_hash, salt=salt, view=view)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('index'))
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        error = 'Invalid username or password'
    return render_template('index.html', error=error)
    
@app.route('/login', methods=['POST'])
def login():
    error = None
    try:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first_or_404()
        m = hashlib.md5()
        m.update(user.salt)
        m.update(password)
        _hash = m.digest()
        
        if _hash == user._hash:
            session['logged_in'] = True
        else:
            error = 'Invalid username or password'
    except:
        print 'login failed'
        session['username'] = None
        session['password'] = None
        session['bmo'] = None
        error = 'Invalid username or password'
    return redirect(url_for('index'), error=error)
    
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
    init_db()
    app.run()
    
from relmandash.models import *
