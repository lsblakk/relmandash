from relmandash import app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence, ForeignKey

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    hash = db.Column(db.String(50), nullable=False)
    salt = db.Column(db.String(50), nullable=False)
    default_view = db.Column(db.String(50))

    def __init__(self, email, _hash, salt, view):
        self.email = email
        self.hash = _hash
        self.salt = salt
        self.default_view = view
        
    def __repr__(self):
        return '<User %r>' % self.email
    
class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    
    def __init__(self, id, description):
        self.id = id
        self.description = description
        
    def __repr__(self):
        return '<Product %r>' % self.description

class Component(db.Model):
    __tablename__ = 'Components'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    product = db.Column(None, ForeignKey('Products.id'), nullable=False)
    
    def __init__(self, id, description, product):
        self.id = id
        self.description = description
        self.product = product
        
    def __repr__(self):
        return '<Component %r from Product %r>' % (self.description, self.product)

class View(db.Model):
    __tablename__ = 'Views'
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    
    def __init__(self, id, description):
        self.id = id
        self.description = description
        
    def __repr__(self):
        return '<View %r>' % self.description
        
class ViewComponent(db.Model):
    __tablename__ = 'View_Components'
    view = db.Column(None, ForeignKey('Views.id'), primary_key=True)
    component = db.Column(None, ForeignKey('Components.id'), primary_key=True)
    
    def __init__(self, view, component):
        self.view = view
        self.component = component
        
    def __repr__(self):
        return '<View %r with Component %r>' % (self.view, self.component)

class ViewMember(db.Model):
    __tablename__ = 'View_Members'
    view = db.Column(None, ForeignKey('Views.id'), primary_key=True)
    member = db.Column(None, ForeignKey('Users.id'), primary_key=True)
    
    def __init__(self, view, member):
        self.view = view
        self.member = member
        
    def __repr__(self):
        return '<View %r with Member %r>' % (self.view, self.member)

class ViewOwner(db.Model):
    __tablename__ = 'View_Owners'
    view = db.Column(None, ForeignKey('Views.id'), primary_key=True)
    owner = db.Column(None, ForeignKey('Users.id'), primary_key=True)
    
    def __init__(self, view, owner):
        self.view = view
        self.owner = owner
        
    def __repr__(self):
        return '<View %r with Owner %r>' % (self.view, self.owner)
