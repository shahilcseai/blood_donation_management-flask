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

with app.app_context():
    # Import routes after the app is created to avoid circular imports
    from routes import *
    # Create all database tables
    db.create_all()
