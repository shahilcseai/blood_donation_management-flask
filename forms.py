from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, BooleanField, DateField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from datetime import datetime, timedelta

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('donor', 'Donor'), ('recipient', 'Recipient')], validators=[DataRequired()])

class DonorProfileForm(FlaskForm):
    blood_type = SelectField('Blood Type', choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    last_donation = DateField('Last Donation Date', validators=[Optional()])
    medical_conditions = TextAreaField('Medical Conditions')
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=10)])
    agree_to_terms = BooleanField('I agree to the terms and conditions', validators=[DataRequired()])

class DonorSearchForm(FlaskForm):
    blood_type = SelectField('Blood Type', choices=[
        ('', 'Any'),
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    zip_code = StringField('ZIP Code', validators=[Optional()])
    radius = IntegerField('Search Radius (miles)', validators=[Optional(), NumberRange(min=1, max=100)])

class BloodRequestForm(FlaskForm):
    blood_type = SelectField('Blood Type', choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    hospital_name = StringField('Hospital Name', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    emergency = BooleanField('This is an emergency request')
    notes = TextAreaField('Additional Notes')

class InventoryUpdateForm(FlaskForm):
    blood_type = SelectField('Blood Type', choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    operation = SelectField('Operation', choices=[('add', 'Add'), ('remove', 'Remove')], validators=[DataRequired()])

class DonationScheduleForm(FlaskForm):
    donation_date = DateField('Preferred Donation Date', 
                            validators=[DataRequired()],
                            default=datetime.utcnow() + timedelta(days=1))