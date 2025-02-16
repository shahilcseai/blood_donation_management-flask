from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)  # 'donor', 'recipient', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(200))  # New: For location-based search
    latitude = db.Column(db.Float)  # New: For location-based search
    longitude = db.Column(db.Float)  # New: For location-based search

    # Relationships
    donor_profile = db.relationship('DonorProfile', backref='user', lazy=True, uselist=False)
    blood_requests = db.relationship('BloodRequest', backref='recipient', lazy=True)
    health_records = db.relationship('DonorHealthRecord', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_type = db.Column(db.String(5), nullable=False)
    quantity_ml = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class DonorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    last_donation = db.Column(db.DateTime)
    total_donations = db.Column(db.Integer, default=0)
    availability_status = db.Column(db.String(20), default='available')
    medical_conditions = db.Column(db.Text)
    last_health_check = db.Column(db.DateTime)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    quantity_ml = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, completed, rejected
    emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hospital_name = db.Column(db.String(128), nullable=False)  # New field
    contact_number = db.Column(db.String(15), nullable=False)  # New field
    notes = db.Column(db.Text)  # New field

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New: Health tracking for donors
class DonorHealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    hemoglobin = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    pulse_rate = db.Column(db.Integer)
    weight = db.Column(db.Float)
    last_meal = db.Column(db.DateTime)
    iron_level = db.Column(db.Float)
    notes = db.Column(db.Text)