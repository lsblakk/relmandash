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
    initializeSession()
    session['last_url'] = 'index'
    message = ''
    email = request.args.get('email')
    product = request.args.get('product')
    components = request.args.getlist('component')
    style = request.args.get('style')
    if email:
        return view_individual(email)
    elif product:
        return view_prodcomp(product=product, components=components, style=style)
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
    print 'login'
    session['logged_in'] = True
    session['user'] = user
    session['bmo'] = BMOAgent(user.email, password)
    return redirect(url_for('index'))

def create_view(user, request):
    view_name = request.form['viewname']
    view_desc = request.form['description']
    view_default = request.form['default']
    view_comps = request.form.getlist('components')
    view_emails = request.form.getlist('emails')
    default = False
    
    if not view_comps and len(view_emails) == 1 and view_emails[0] == '':
        raise Exception('Empty view not allowed')
    
    if view_default == 'yes':
        default = True
        user = User.query.filter_by(id=user.id).first()
        for view in user.views:
            view.default = False
        
    view = View(view_name, view_desc, default, user)
    db.session.add(view)
    
    for component_id in view_comps:
        view.components.append(Component.query.filter_by(id=component_id).first())
    for member in view_emails:
        if member != '':
            view.members.append(Member(member))
    db.session.commit()

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
            if email == '' or password == '':
                raise Exception('User must have an email and a password!')
            
            if password != request.form['confirmpassword']:
                raise Exception('Please re-enter the same password')
                
            try:
                # verify email and password
                bmo = BMOAgent(email, password)
                bug = bmo.get_bug('80000')
            except Exception, e:
                raise Exception('Failed to verify Bugzilla account on Bugzilla server:' + e)
        
            #generate salt, hash and store to db
            salt = os.urandom(8)
            m = hashlib.md5()
            m.update(salt)
            m.update(password)
            _hash = m.digest()
            user = User(email=email, _hash=_hash.encode('base64'), salt=salt.encode('base64'))
            db.session.add(user)
            db.session.commit()
            print 'creating'
            create_view(user, request)
            
            return loginSession(user, password)
    except Exception, e:
        print e
        if error == None:
            error = e
    return render_template('index.html', error=error)
    
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
    
@app.route('/edit_account', methods=['POST'])
def edit_account():
    try:
        email = request.form['email']
        password = request.form['password']
        user = session['user']
        
        if verify_account(user, password):
            newpassword = request.form['newpassword']
            
            if newpassword != request.form['confirmpassword']:
                raise Exception('Please re-enter the same password')
            
            if newpassword == '':
                bmo = BMOAgent(email, password)
                bug = bmo.get_bug('80000')
            else:
                bmo = BMOAgent(email, newpassword)
                bug = bmo.get_bug('80000')
                salt = os.urandom(8)
                m = hashlib.md5()
                m.update(salt)
                m.update(password)
                _hash = m.digest()
                user.hash = _hash
                user.salt = salt
                
            user.email = email
            db.session.commit()
            return redirect(url_for('profile', message='Account updated'))
    except Exception, e:
        error = e
        return render_template('index.html', error=error)
        
@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    try:
        if request.method == 'GET':
            return render_template('delete.html')
        else:
            password = request.form['password']
            user = session['user']
            if verify_account(user, password):
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for('logout', message='Account deleted'))
            else:
                raise Exception('Incorrect password, failed to delete account.')
    except Exception, e:
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
def profile(email, message=''):
    error = 'You are not authorized to view this page. Please log in to continue...'
    views = None
    try:
        user = session['user']
        if email != user.email:
            raise Exception('You are only authorized to view your own profile!')
        products = Product.query.order_by(Product.description).all()
        defaultview = View.query.filter_by(owner_id=user.id).filter_by(default=True).first()
        otherviews = View.query.filter_by(owner_id=user.id).filter_by(default=False).all()
        return render_template('profile.html', products=products, defaultview=defaultview, otherviews=otherviews, message=message)
    except Exception, e:
        error = e
    return render_template('profile.html', error=error)
    
@app.route('/add_view', methods=['GET', 'POST'])
def add_view():
    error = None
    try:
        if request.method == 'GET':
            products = Product.query.order_by(Product.description).all()
            return render_template('addview.html', products=products)
        else:
            user = session['user']
            create_view(user, request)
            return redirect(url_for('profile', email=user.email))
    except Exception, e:
        if error == None:
            error = e
    return render_template('index.html', error=error)
    
@app.route('/edit_views/<int:view_id>', methods=['POST'])
def edit_views(view_id):
    error = ''
    try:
        if request.form['submit'] == 'Delete view':
            view = View.query.filter_by(id=view_id).first()
            db.session.delete(view)
            db.session.commit()
        else:
            view = View.query.filter_by(id=view_id).first()
            membersToRemove = request.form.getlist('membersToRemove')
            
            for memb in membersToRemove:
                members = [item for item in view.members if item.email == memb]
                if members:
                    view.members.remove(members[0])
                    
            compsToRemove = request.form.getlist('compsToRemove')
            for comp in compsToRemove:
                components = [item for item in view.components if item.id == int(comp)]
                if components:
                    view.components.remove(components[0])
            
            view_name = request.form['viewname']
            view_desc = request.form['description']
            view_comps = request.form.getlist('components')
            view_emails = request.form.getlist('emails')
            view_default = request.form['default']
            
            for component_id in view_comps:
                view.components.append(Component.query.filter_by(id=component_id).first())
            for member in view_emails:
                if member != '':
                    view.members.append(Member(member))
            
            if view_default == 'yes':
                if not view.components and not view.members:
                    raise Exception('Empty default view not allowed')
                
                user = User.query.filter_by(id=session['user'].id).first()
                for _view in user.views:
                    _view.default = False
                view.default = True
            
            db.session.commit()
        return redirect(url_for('profile', email=session['user'].email))
    except Exception, e:
        error = e
    return render_template('index.html', error=error)

@app.route('/view_custom/<int:view_id>')
def view_custom(view_id):
    try:
        view = View.query.filter_by(id=view_id).first()
        if view == None:
            raise Exception('Invalid view')
        members = ""
        for member in view.members:
            members = members + member.email + ", "
        prodcompmap = {}
        for component in view.components:
            if prodcompmap.has_key(component.product.description):
                prodcompmap[component.product.description] = prodcompmap[component.product.description] + ", " + component.description
            else:
                prodcompmap[component.product.description] = component.description
        return render_template('team.html', view=view, members=members, prodcompmap=prodcompmap)
    except Exception, e:
        error = e
    return render_template('index.html', error=error)
    
def getProdCompBugs(product, components):
    print product
    print components
    bmo = initializeSession()
    vt = session['vt']
    options = getProdComp(product, components, vt.beta, vt.aurora, vt.esr)
    buglist = bmo.get_bug_list(options)
    for bug in buglist:
        print bug.id
    return buglist

def getAssignedBugs(emails):
    bmo = initializeSession()
    options = getAssignedOptions(emails)
    mainlist = bmo.get_bug_list(options)
    return mainlist

def getToFollowBugs(emails):
    bmo = initializeSession()
    vt = session['vt']
    followUpOptions = getToFollowUp(emails, vt.beta, vt.aurora)
    followlist = bmo.get_bug_list(followUpOptions)
    return followlist
    
"""
    INDIVIDUAL ROUTING
"""
def view_individual(email):
    error = ''
    mainlist=[]
    followlist=[]
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    if pattern.match(email):
        try:
            bmo = initializeSession()
            options = getAssignedOptions(email)
            mainlist = bmo.get_bug_list(options)
            session['vt'] = vt = VersionTracker()
            
            followUpOptions = getToFollowUp(email, vt.beta, vt.aurora)
            followlist = bmo.get_bug_list(followUpOptions)
            print len(mainlist)
            print len(followlist)
        except AttributeError, e:
            print 'View Individual: ' + str(e)
            error = e
        except Exception, e:
            error = e
    else:
        error = 'Invalid email address'
    return render_template('individual.html', error=error, email=email, mainlist=mainlist, followlist=followlist)

"""
    PRODUCT/COMPONENT ROUTING
"""
def view_prodcomp(product, components=[], style=''):
    try:
        error = ''
        prod = Product.query.filter_by(description=product).first()
        if product is None:
            raise Exception('Invalid product')
        session['vt'] = vt = VersionTracker()
        componentsSentence = ''
        if len(components) > 0:
            for component in components:
                compquery = [item for item in prod.components if item.description == component]
                if len(compquery) == 0:
                    error = 'One or more components entered is invalid'
                else:
                    componentsSentence = componentsSentence + ', ' + component
        
        if components == [] or componentsSentence != '':
            bmo = session['bmo']
            buglist = bmo.get_bug_list(getProdComp(product, componentsSentence, vt.beta, vt.aurora, vt.esr))
            
            if len(buglist) > 0:
                if style == 'table':
                    return render_template('prodcomptable.html', product=prod, query_components=components, buglist=buglist, error=error)
                elif style == 'count':
                    return render_template('prodcompcount.html', product=prod, query_components=components, beta=beta, aurora=aurora, esr=esr, unassigned=unassigned, info=info)
                else:
                    return render_template('prodcomplist.html', product=prod, query_components=components, buglist=buglist, error=error)
            else:
                raise Exception('Looks like there are no tracked bugs for this product/component!')
    except Exception, e:
        error = e
    return render_template('prodcomplist.html', error=error)     

@app.route('/logout')
def logout(message=''):
    session.clear()
    if not message:
        message = 'You are now logged out'
    return render_template('index.html', message=message)
    
app.jinja_env.globals.update(getTrackedBugs=getTrackedBugs)
app.jinja_env.globals.update(getAssignedBugs=getAssignedBugs)
app.jinja_env.globals.update(getUnassignedBugs=getUnassignedBugs)
app.jinja_env.globals.update(getProdCompBugs=getProdCompBugs)
app.jinja_env.globals.update(getNeedsInfoBugs=getNeedsInfoBugs)
app.jinja_env.globals.update(getToFollowBugs=getToFollowBugs)
app.jinja_env.globals.update(getToNominateBugs=getToNominateBugs)
app.jinja_env.globals.update(getToApproveBugs=getToApproveBugs)
app.jinja_env.globals.update(getToUpliftBugs=getToUpliftBugs)
app.jinja_env.globals.update(getKeywords=getKeywords)
app.jinja_env.globals.update(getComponents=getComponents)

def initializeSession():
    try:
        bmo = session['bmo']
        session['vt'] = VersionTracker()
    except:
        bmo = session['bmo'] = BMOAgent('','')
        session['vt'] = VersionTracker()
    return bmo

if __name__ == '__main__':
    session.clear()
    app.run()
    
from relmandash.models import *
