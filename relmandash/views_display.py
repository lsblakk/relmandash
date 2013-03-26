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
from utils import *
from models import *

def view_individual(email):
    error = ''
    mainlist=[]
    followlist=[]
    pattern = re.compile('^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,6}$')
    try:
        if pattern.match(email):
            mainlist = getAssignedBugs(email)
            followlist = getToFollowBugs(email)
            print len(mainlist)
            print len(followlist)
        else:
            raise Exception('Invalid email address')
    except Exception, e:
        error = 'Individual view: ' + str(e)
    return render_template('individual.html', error=error, email=email, buglist=mainlist, followlist=followlist)

def view_prodcomp(product, components=[], style=''):
    error = ''
    prod = None
    buglist = []
    try:
        initializeSession()
        vt = session['vt']
        
        prod = Product.query.filter_by(description=product).first()
        if product is None:
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
            buglist = bmo.get_bug_list(getProdComp(product, componentsSentence, vt))
            if len(buglist) == 0:
                raise Exception('Looks like there are no tracked bugs for this product/component!')
    except Exception, e:
        error = 'Product view: ' + str(e)
    return render_template('prodcomplist.html', product=prod, query_components=components, buglist=buglist, style=style, error=error)

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
    except Exception, e:
        error = e
    return redirect(url_for('profile', email=session['user'].email, error=error))
    
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
        error = ''
    return render_template('index.html', message=message, error=error)
