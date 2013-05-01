'''
    Reference: http://pythonhosted.org/Flask-SQLAlchemy/quickstart.html
'''
from relmandash import app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence, ForeignKey

db = SQLAlchemy(app)

class Component(db.Model):
    __tablename__ = 'Components'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    product_id = db.Column(None, db.ForeignKey('Products.id'), nullable=False)
    
    def __init__(self, id, description, product):
        self.id = id
        self.description = description
        self.product = product
        
    def __repr__(self):
        return '<Component %r from Product %r>' % (self.description, self.product)

class Query(db.Model):
    __tablename__ = 'Queries'
    id = db.Column(db.Integer, Sequence('query_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    show_summary = db.Column(db.Boolean, nullable=False)
    url = db.Column(db.Text)
    runtime = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    
    def __init__(self, name, description, show_summary, url, runtime, owner):
        self.name = name
        self.description = description
        self.show_summary = show_summary
        self.url = url
        self.runtime = runtime
        self.owner = owner
        
    def __repr__(self):
        return '<Query %r: %r URL: %r Runtime: %r>' % (self.name, self.description, self.url, self.runtime)

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    
    components = db.relationship("Component", backref='product', cascade="all, delete, delete-orphan")
    
    def __init__(self, id, description):
        self.id = id
        self.description = description
        
    def __repr__(self):
        return '<Product %r>' % self.description

ViewComponent = db.Table(
    'Views_Components',
    db.Column('view_id', db.Integer, db.ForeignKey('Views.id')),
    db.Column('component_id', db.Integer, db.ForeignKey('Components.id'))
)

ViewMember = db.Table(
    'Views_Members',
    db.Column('view_id', db.Integer, db.ForeignKey('Views.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('Members.id'))
)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(100), nullable=False)
    
    views = db.relationship("View", backref='owner', cascade="all, delete, delete-orphan")
    queries = db.relationship("Query", backref='owner', cascade="all, delete, delete-orphan")

    def __init__(self, email, _hash, salt):
        self.email = email
        self.hash = _hash
        self.salt = salt
        
    def __repr__(self):
        return '<User %r>' % self.email
    
class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, Sequence('member_id_seq'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    
    def __init__(self, email):
        self.email = email
        
    def __repr__(self):
        return '<Member %r>' % self.email

class View(db.Model):
    __tablename__ = 'Views'
    id = db.Column(db.Integer, Sequence('view_id_seq'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    default = db.Column(db.Boolean, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    
    # many to many View <-> Component
    components = db.relationship('Component', secondary=ViewComponent, backref='view')
    members = db.relationship('Member', secondary=ViewMember, backref='view', cascade="all, delete")
    
    def __init__(self, name, description, default, owner):
        self.name = name
        self.description = description
        self.default = default
        self.owner = owner
        
    def __repr__(self):
        return '<View %r -> %r>' % (self.name, self.description)
