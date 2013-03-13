'''
    Reference: http://pythonhosted.org/Flask-SQLAlchemy/quickstart.html
'''
from relmandash import app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence, ForeignKey

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(100), nullable=False)

    def __init__(self, email, _hash, salt):
        self.email = email
        self.hash = _hash
        self.salt = salt
        
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
    product_id = db.Column(None, ForeignKey('Products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('components', lazy='dynamic'))
    
    def __init__(self, id, description, product):
        self.id = id
        self.description = description
        self.product = product
        
    def __repr__(self):
        return '<Component %r from Product %r>' % (self.description, self.product)

class View(db.Model):
    __tablename__ = 'Views'
    id = db.Column(db.Integer, Sequence('view_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    default = db.Column(db.Boolean, nullable=False)
    owner_id = db.Column(None, ForeignKey('Users.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('views', lazy='dynamic'))
    
    def __init__(self, name, description, default, owner):
        self.name = name
        self.description = description
        self.default = default
        self.owner = owner
        
    def __repr__(self):
        return '<View %r owned by %r>' % (self.description, self.owner_id)
        
class ViewComponent(db.Model):
    __tablename__ = 'View_Components'
    view_id = db.Column(None, ForeignKey('Views.id'), primary_key=True)
    component_id = db.Column(None, ForeignKey('Components.id'), primary_key=True)
    view = db.relationship('View', backref=db.backref('view_components', lazy='dynamic'))
    
    def __init__(self, view, component_id):
        self.view = view
        self.component_id = component_id
        
    def __repr__(self):
        return '<View %r with Component %r>' % (self.view, self.component)

class ViewMember(db.Model):
    __tablename__ = 'View_Members'
    view_id = db.Column(None, ForeignKey('Views.id'), primary_key=True)
    email = db.Column(db.String(100), nullable=False, primary_key=True)
    view = db.relationship('View', backref=db.backref('view_members', lazy='dynamic'))
    
    def __init__(self, view, email):
        self.view = view
        self.email = email
        
    def __repr__(self):
        return '<View %r with Member %r>' % (self.view, self.member)
