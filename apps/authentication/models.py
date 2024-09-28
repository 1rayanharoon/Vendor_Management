# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.LargeBinary)
    account_type = db.Column(db.String(64))  # New field for account type

    oauth_github  = db.Column(db.String(100), nullable=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)
    
#create vendor class like above with basic information like location, name and contact
class Vendor(db.Model):
    __tablename__ = 'Vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    contact_person_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    head_name = db.Column(db.String(100), nullable=False)
    head_designation = db.Column(db.String(100), nullable=False)
    head_email = db.Column(db.String(100), nullable=False)
    head_phone_number = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Vendor('{self.name}', '{self.address}', '{self.city}, '{self.contact_person_name}', '{self.designation}', '{self.contact_number}, '{self.phone_number}', '{self.head_name}', '{self.head_designation}', '{self.head_email}', '{self.head_phone_number}')"
    

class Article(db.Model):
    __tablename__ = 'Articles'

    Category = db.Column(db.String, nullable=False)
    Product_Name = db.Column(db.String(100), nullable=False)
    Article_No = db.Column(db.String(100), primary_key=True)
    Gender = db.Column(db.String(100), nullable=False)
    Color = db.Column(db.String(100), nullable=False)
    Size = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(100), nullable=False)
    Client_Name = db.Column(db.String(64))
    images = db.relationship('ArticleImage', backref='article', lazy='dynamic')
 

    def __repr__(self):
        return f"Article('{self.Category}', '{self.Product_Name}', '{self.Article_No}', '{self.Gender}', '{self.Color}', '{self.Size}', '{self.Description}', '{self.Client_Name}')"


class ArticleImage(db.Model):
    __tablename__ = 'ArticleImages'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('Articles.Article_No'), nullable=False)

class Client(db.Model):
    __tablename__ = 'Clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    contact_person_name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    contact_number = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    head_name = db.Column(db.String(100))
    head_designation = db.Column(db.String(100))
    head_email = db.Column(db.String(100))
    head_phone_number = db.Column(db.String(50))

    def __repr__(self):
        return f"Clients('{self.name}', '{self.address}', '{self.city}, '{self.contact_person_name}', '{self.designation}', '{self.contact_number}, '{self.phone_number}', '{self.head_name}', '{self.head_designation}', '{self.head_email}', '{self.head_phone_number}')"


class Inspector(db.Model):
    __tablename__ = 'Inspector'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"Inspector('{self.name}', '{self.location}', '{self.contact}', '{self.email}')"

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)
