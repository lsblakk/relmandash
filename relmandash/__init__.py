from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack, jsonify
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
import re
from dashboard.options import *
from dashboard.versions import *
#from dashboard.products import *
from utils import *
import os
import hashlib
from flask.ext.sqlalchemy import SQLAlchemy

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
    if 'bmo' not in session.keys():
        print 'no bmo'
        session['bmo'] = BMOAgent('','')
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

def loginSession(user, password):
    session['logged_in'] = True
    session['user'] = user
    session['bmo'] = BMOAgent(user.email, password)
    return redirect(url_for('index')+'?'+view)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    try:
        if request.method == 'GET':
            products = Product.query.order_by(Product.description).all()
            return render_template('signup.html', products=products)
        else:
            email = request.form['email']
            user = User.query.filter_by(email=email).first()
        
            if user != None:
                raise Exception('User email already exists')
            
            password = request.form['password']
            
            if password != request.form['confirmpassword']:
                raise Exception('Please re-enter the same password')
                
            # verify email and password
            bmo = BMOAgent(email, password)
            bug = bmo.get_bug('80000')
        
            #generate salt, hash and store to db
            salt = os.urandom(8)
            m = hashlib.md5()
            m.update(salt)
            m.update(password)
            _hash = m.digest()
            user = User(email=email, _hash=_hash.encode('base64'), salt=salt.encode('base64'))
            db.session.add(user)
            
            #create view
            view_name = request.form['viewname']
            view_desc = request.form['description']
            view_comps = request.form.getlist('components')
            view_emails = request.form.getlist('emails')
            view = View(view_name, view_desc, True, user)
            db.session.add(view)
            
            for component_id in view_comps:
                view_component = ViewComponent(view, int(component_id))
                db.session.add(view_component)
            for member in view_emails:
                view_member = ViewMember(view, member)
                db.session.add(view_member)
            db.session.commit()
            return loginSession(user, password)
    except Exception, e:
        print e
        if error == None:
            error = e
    return render_template('index.html', error=error)
    
@app.route('/login', methods=['POST'])
def login():
    error = None
    try:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user == None:
            raise Exception('Invalid Bugzilla email entered')
        
        m = hashlib.md5()
        m.update(user.salt.decode('base64'))
        m.update(password)
        _hash = m.digest()
        
        if _hash != user.hash.decode('base64'):
            raise Exception('Invalid password')
        else:
            return loginSession(user, password)
    except Exception, e:
        print 'login failed'
        session['bmo'] = None
        error = e
    return render_template('index.html', error=error)
    
@app.route('/profile/<string:email>')
def profile(email):
    error = 'You are not authorized to view this page. Please log in to continue...'
    views = None
    try:
        user = session['user']
        if email != user.email:
            raise Exception('You are only authorized to view your own profile!')
        products = Product.query.order_by(Product.description).all()
        #views = db.session.query(View).join(ViewComponent).filter(View.owner_id==user.id).join(Component).join(Product).all()
        views_joined = db.session.query(View, ViewComponent, Component, Product).filter(View.id==ViewComponent.view_id).filter(ViewComponent.component_id==Component.id).filter(Component.product_id==Product.id).filter(View.owner_id==user.id).all()
        default = View.query.filter_by(owner_id=user.id).filter_by(default=True).first()
        return render_template('profile.html', products=products, views_joined=views_joined, default=default)
    except Exception, e:
        error = e
    return render_template('profile.html', error=error)
    
@app.route('/edit_views/<int:view_id>', methods=['POST'])
def edit_views(view_id):
    error = ''
    try:
        membersToRemove = request.form.getlist('membersToRemove')
        for emailm in membersToRemove:
            member = ViewMember.query.filter_by(view_id=view_id).filter_by(email=emailm).first()
            db.session.delete(member)
        compsToRemove = request.form.getlist('compsToRemove')
        for comp in compsToRemove:
            component = ViewComponent.query.filter_by(view_id=view_id).filter_by(component_id=comp).first()
            db.session.delete(component)
        view_comps = request.form.getlist('components')
        view_emails = request.form.getlist('emails')
        view = View.query.filter_by(id=view_id)
        
        for component_id in view_comps:
            view_component = ViewComponent(view, int(component_id))
            db.session.add(view_component)
        for member in view_emails:
            view_member = ViewMember(view, member)
            db.session.add(view_member)
        db.session.commit()
        redirect(url_for('profile', email=session['user'].email))
    except Exception, e:
        error = e
    return render_template('index.html', error=error)
    
"""
    INDIVIDUAL ROUTING
"""
def view_individual(email):
    error = ''
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    if pattern.match(email):
        try:
            bmo = session['bmo'] = BMOAgent(session['email'], session['password'])
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
def view_prodcomp(product, component='', style=''):
    error = 'Invalid product or component'
    session['vt'] = vt = VersionTracker()
    try:
        prod = Product.query.filter_by(description=product).first()
        if product is not None:
            print product
            comp = None
            if component is None:
                component = ''
            else:
                comp = Component.query.join(Product).filter(Product.description==product).filter(Component.description==component).first()
            
            if component == '' or comp is not None:
                bmo = session['bmo']
                buglist = bmo.get_bug_list(getProdComp(product, component, vt.beta, vt.aurora, vt.esr))
                
                if len(buglist) > 0:
                    if style == 'table':
                        return render_template('prodcomptable.html', product=product, component=component, buglist=buglist, aurora=aurora, esr=esr, unassigned=unassigned, info=info, keywords=keywords)
                    elif style == 'count':
                        return render_template('prodcompcount.html', product=product, component=component, beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info, components=components)
                    else:
                        return render_template('prodcomplist.html', product=product, component=component, buglist=buglist)
                else:
                    error = 'Looks like there are no tracked bugs for this product/component!'
    except Exception, e:
        error = e
    return render_template('prodcomplist.html', error=error)     

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('bmo', None)
    message = 'You are now logged out'
    return render_template('index.html', message=message)
    
app.jinja_env.globals.update(getTrackedBugs=getTrackedBugs)
app.jinja_env.globals.update(getUnassignedBugs=getUnassignedBugs)
app.jinja_env.globals.update(getNeedsInfoBugs=getNeedsInfoBugs)
app.jinja_env.globals.update(getKeywords=getKeywords)
app.jinja_env.globals.update(getComponents=getComponents)

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
