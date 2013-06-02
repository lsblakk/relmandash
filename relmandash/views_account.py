from relmandash import app, db

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack, jsonify
from bugzilla.agents import BMOAgent
import re
from dashboard.options import *
from dashboard.versions import *
from dashboard.utils import *
import os
import hashlib
from models import *
from utils import *

'''
    non-views used by view functions
'''
def loginSession(user, password):
    initializeSession()
    session['logged_in'] = True
    session['user'] = user
    session['bmo'] = BMOAgent(user.email, password)
    session.permanent = True
    view = View.query.filter_by(default=True).filter_by(owner_id=user.id).first()
    return redirect(url_for('view_custom', view_id=view.id))



def view_prodcomp(product, components=[], style=''):
    error = ''
    prod = None
    buglist = []
    try:
        initializeSession()
        vt = session['vt']
        
        prod = Product.query.filter_by(description=product).first()
        if prod is None:
            raise Exception('Invalid product')
            
        componentsSentence = ''
        if len(components) > 0:
            for component in components:
                compquery = [item for item in prod.components if item.description == component]
                if len(compquery) == 0:
                    error = 'Product view: One or more components entered is invalid'
                else:
                    componentsSentence = componentsSentence + ', ' + component
        
        if components == [] or componentsSentence != '':
            bmo = session['bmo']
            try:
                buglist = bmo.get_bug_list(getProdComp(product, componentsSentence, vt))
            except:
                raise Exception('Bad query: Possible reasons might include bad authentication, results too large, or just plain bad query.')
    except Exception, e:
        error = 'Product view: ' + str(e)
    return render_template('prodcomplist.html', error=error, product=prod, query_components=components, buglist=buglist, style=style)

def create_view(user, request):
    try:
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
    except Exception, e:
        raise Exception('Failed to create view: ' + str(e))

def create_query(user, request):
    try:
        query_name = request.form['queryname']
        query_desc = request.form['description']
        query_url = request.form['url']
        query_runtime = request.form['runtime']
        query_show_summary = request.form['show_summary']
        default = False
        
        if query_url == '' or query_desc == '':
            raise Exception('Empty query not allowed')
            
        query = Query(query_name, query_desc, query_show_summary, query_url, query_runtime, user)
        db.session.add(query)

        db.session.commit()
    except Exception, e:
        raise Exception('Failed to create query: ' + str(e))

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
    
    
'''
    ACCOUNT RELATED
'''

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

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    try:
        initializeSession()
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
        
@app.route('/edit_account', methods=['POST'])
def edit_account():
    error = ''
    message = ''
    email = ''
    try:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=session['user'].email).first()
        print user.email
        
        if verify_account(user, password):
            newpassword = request.form['newpassword']
            print 'shit'
            if newpassword != request.form['confirmpassword']:
                raise Exception('Please re-enter the same password')
            print 'dshit'
            if newpassword == '':
                bmo = BMOAgent(email, password)
                bug = bmo.get_bug('80000')
            else:
                
                session['bmo'] = bmo = BMOAgent(email, newpassword)
                bug = bmo.get_bug('80000')
                salt = os.urandom(8)
                m = hashlib.md5()
                m.update(salt)
                m.update(password)
                _hash = m.digest()
                user.hash = _hash.encode('base64')
                user.salt = salt.encode('base64')
                
            user.email = email
            db.session.commit()
            session['user'] = user
            message = 'Account updated'
    except Exception, e:
        error = e
    return profile(email=email, message=message, error=error)

@app.route('/logout')
def logout(message=''):
    session.clear()
    initializeSession()
    if not message:
        message = 'You are now logged out'
    return render_template('index.html', message=message)
    
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    try:
        initializeSession()
        if request.method == 'GET':
            return render_template('login.html')
        else:
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
def profile(email, message='', error=''):
    products = None
    defaultview = None
    otherviews = None
    print message
    print error
    try:
        initializeSession()
        try:
            user = session['user']
        except:
            raise Exception('You are not authorized to view this page. Please log in to continue...')
        if email != user.email:
            raise Exception('You are only authorized to view your own profile!')
        products = Product.query.order_by(Product.description).all()
        defaultview = View.query.filter_by(owner_id=user.id).filter_by(default=True).first()
        otherviews = View.query.filter_by(owner_id=user.id).filter_by(default=False).all()
        queries = Query.query.filter_by(owner_id=user.id).all()
    except Exception, e:
        error = e
    return render_template('profile.html', products=products, defaultview=defaultview, otherviews=otherviews, queries=queries, message=message, error=error)


'''
        QUERIES 
'''

@app.route('/add_query', methods=['GET', 'POST'])
def add_query():
    error = None
    email=''
    message = ''
    error = ''
    try:
        initializeSession()
        if request.method == 'GET':
            return render_template('addquery.html')
        else:
            user = session['user']
            create_query(user, request)
            email = user.email
            message = 'New query created!'
    except Exception, e:
        error = e
    return redirect(url_for('profile', email=email, message=message, error=error))
 
@app.route('/edit_query/<int:query_id>', methods=['POST'])
def edit_query(query_id):
    error = ''
    message = ''
    email = ''
    try:
        initializeSession()
        if request.form['submit'] == 'Delete query':
            query = Query.query.filter_by(id=query_id).first()
            db.session.delete(query)
            db.session.commit()
        else:
            query = Query.query.filter_by(id=query_id).first()
            if query is not None:
                query.name = request.form['queryname']
                query.description = request.form['description']
                query.url = request.form['url']
                query.runtime = request.form['runtime']
                query.show_summary = request.form['show_summary']
                db.session.commit()
                message = 'Query updated'
    except Exception, e:
        error = e
    return redirect(url_for('profile', email=session['user'].email, message=message, error=error))


'''
        VIEWS
'''

@app.route('/view_custom/<int:view_id>')
def view_custom(view_id):
    view = None
    members = ""
    prodcompmap = {}
    error = ""
    try:
        initializeSession()
        view = View.query.filter_by(id=view_id).first()
        if view == None:
            raise Exception('Invalid view')
        for member in view.members:
            members = members + member.email + ", "
        for component in view.components:
            if prodcompmap.has_key(component.product.description):
                prodcompmap[component.product.description] = prodcompmap[component.product.description] + ", " + component.description
            else:
                prodcompmap[component.product.description] = component.description
    except Exception, e:
        error = e
    return render_template('team.html', view=view, members=members, prodcompmap=prodcompmap, error=error)
    
@app.route('/add_view', methods=['GET', 'POST'])
def add_view():
    error = None
    email=''
    message = ''
    error = ''
    try:
        initializeSession()
        if request.method == 'GET':
            products = Product.query.order_by(Product.description).all()
            return render_template('addview.html', products=products)
        else:
            user = session['user']
            create_view(user, request)
            email = user.email
            message = 'New view created!'
    except Exception, e:
        error = e
    return redirect(url_for('profile', email=email, message=message, error=error))

@app.route('/edit_views/<int:view_id>', methods=['POST'])
def edit_views(view_id):
    error = ''
    message = ''
    email = ''
    try:
        initializeSession()
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
            message = 'View updated'
    except Exception, e:
        error = e
    return redirect(url_for('profile', email=session['user'].email, message=message, error=error))


@app.route('/')
def index():
    error = ''
    message = ''
    try:
        initializeSession()
        email = request.args.get('email')
        product = request.args.get('product')
        components = request.args.getlist('component')
        style = request.args.get('style')
        if email:
            return view_individual(email)
        elif product:
            return view_prodcomp(product=product, components=components, style=style)
        elif request.args.keys():
            raise Exception('Invalid query!')
    except Exception, e:
        error = e
    return render_template('index.html', message=message, error=error)
