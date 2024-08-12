# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import Email, DataRequired



# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    account_type = SelectField('Account Type', choices=[('Admin', 'Admin'), ('Manager', 'Manager'),('Vendor','Vendor'),('Client','Client')])  # Dropdown for account types



# Add vendor form

class VendorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    business_type = StringField('Business Type', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])



class ArticleForm(FlaskForm):
    Category = SelectField('Category', choices=[
        ('Gloves', 'Gloves'),
        ('Jackets', 'Jackets'),
        ('Trousers', 'Trousers'),
        ('1 Pc Suits', '1 Pc Suits'),
        ('2 Pc Suits', '2 Pc Suits'),
        ('Hoodies', 'Hoodies'),
        ('T-Shirts', 'T-Shirts'),
        ('Air Bag Vests', 'Air Bag Vests'),
        ('Boots', 'Boots'),
        ('Accessories', 'Accessories')
    ], validators=[DataRequired()])
    Product_Name = StringField('Product Name', validators=[DataRequired()])
    Article_Number = StringField('Article Number', validators=[DataRequired()])
    Gender = SelectField('Gender', choices=[
        ('M', 'M'),
        ('F', 'F'),
        ('Y', 'Y'),
        ('Unisex', 'Unisex')
    ], validators=[DataRequired()])
    Color = StringField('Color', validators=[DataRequired()])
    Size = StringField('Size', validators=[DataRequired()])
    Description = StringField('Description', validators=[DataRequired()])
    Article_images = FileField('Images', validators=[
        FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG, JPG, and JPEG images are allowed!')
    ])


class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    business_type = StringField('Business Type', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])