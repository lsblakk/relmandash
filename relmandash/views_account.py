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

def loginSession(user, password):
    initializeSession()
    session['logged_in'] = True
    session['user'] = user
    session['bmo'] = BMOAgent(user.email, password)
    session.permanent = True
    view = View.query.filter_by(default=True).filter_by(owner_id=user.id).first()
    return redirect(url_for('view_custom', view_id=view.id))

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

@app.route('/logout')
def logout(message=''):
    session.clear()
    if not message:
        message = 'You are now logged out'
    return render_template('index.html', message=message)
    
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
def profile(email, message='', error=''):
    products = None
    defaultview = None
    otherviews = None
    try:
        try:
            user = session['user']
        except:
            raise Exception('You are not authorized to view this page. Please log in to continue...')
        if email != user.email:
            raise Exception('You are only authorized to view your own profile!')
        products = Product.query.order_by(Product.description).all()
        defaultview = View.query.filter_by(owner_id=user.id).filter_by(default=True).first()
        otherviews = View.query.filter_by(owner_id=user.id).filter_by(default=False).all()
        return render_template('profile.html', products=products, defaultview=defaultview, otherviews=otherviews, message=message)
    except Exception, e:
        error = e
    return render_template('profile.html', products=products, defaultview=defaultview, otherviews=otherviews, message=message, error=error)
