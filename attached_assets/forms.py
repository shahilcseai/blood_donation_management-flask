from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime, timedelta
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('donor', 'Blood Donor'), ('recipient', 'Blood Recipient')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class DonorProfileForm(FlaskForm):
    blood_type = SelectField('Blood Type', 
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    last_donation = DateField('Last Donation Date', validators=[], format='%Y-%m-%d')
    medical_conditions = StringField('Medical Conditions', validators=[Length(max=256)])
    agree_to_terms = BooleanField('I agree to the donation terms and conditions', validators=[DataRequired()])

class BloodRequestForm(FlaskForm):
    blood_type = SelectField('Blood Type', 
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    emergency = BooleanField('Emergency Request')
    notes = StringField('Additional Notes', validators=[Length(max=256)])
    hospital_name = StringField('Hospital Name', validators=[DataRequired(), Length(max=128)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])

class UpdateInventoryForm(FlaskForm):
    blood_type = SelectField('Blood Type',
                           choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                  ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
                           validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    operation = SelectField('Operation',
                          choices=[('add', 'Add'), ('remove', 'Remove')],
                          validators=[DataRequired()])