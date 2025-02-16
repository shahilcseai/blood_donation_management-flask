import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blood_donation.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_blood_inventory():
    from models import BloodInventory
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    for blood_type in blood_types:
        if not BloodInventory.query.filter_by(blood_type=blood_type).first():
            inventory = BloodInventory(blood_type=blood_type, quantity_ml=0)
            db.session.add(inventory)
    db.session.commit()

with app.app_context():
    # Import routes after the app is created to avoid circular imports
    from routes import *
    # Create all database tables
    db.drop_all()  # Drop existing tables
    db.create_all()  # Create new tables with updated schema
    init_blood_inventory()  # Initialize blood inventory