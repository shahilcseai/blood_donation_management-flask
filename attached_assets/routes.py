from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import app, db
from models import User, BloodInventory, DonorProfile, BloodRequest, Notification
from forms import LoginForm, RegisterForm, DonorProfileForm, BloodRequestForm, UpdateInventoryForm
import logging

@app.route('/')
def home():
    inventory = BloodInventory.query.all()
    return render_template('home.html', inventory=inventory)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/donor/profile/create', methods=['GET', 'POST'])
@login_required
def create_donor_profile():
    if current_user.role != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    existing_profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
    if existing_profile:
        return redirect(url_for('donor_dashboard'))

    form = DonorProfileForm()
    if form.validate_on_submit():
        profile = DonorProfile(
            user_id=current_user.id,
            blood_type=form.blood_type.data,
            last_donation=None,
            total_donations=0
        )
        db.session.add(profile)
        db.session.commit()
        flash('Donor profile created successfully!', 'success')
        return redirect(url_for('donor_dashboard'))
    return render_template('donor/create_profile.html', form=form)

@app.route('/donor/dashboard')
@login_required
def donor_dashboard():
    if current_user.role != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('create_donor_profile'))
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    return render_template('donor/dashboard.html', profile=profile, notifications=notifications)

@app.route('/recipient/dashboard')
@login_required
def recipient_dashboard():
    if current_user.role != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    requests = BloodRequest.query.filter_by(recipient_id=current_user.id).order_by(BloodRequest.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    return render_template('recipient/dashboard.html', requests=requests, notifications=notifications)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    inventory = BloodInventory.query.all()
    requests = BloodRequest.query.order_by(BloodRequest.emergency.desc(), BloodRequest.created_at.desc()).all()
    return render_template('admin/dashboard.html', inventory=inventory, requests=requests)

@app.route('/request-blood', methods=['GET', 'POST'])
@login_required
def request_blood():
    if current_user.role != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    form = BloodRequestForm()
    if form.validate_on_submit():
        try:
            request = BloodRequest(
                recipient_id=current_user.id,
                blood_type=form.blood_type.data,
                quantity_ml=form.quantity_ml.data,
                emergency=form.emergency.data,
                hospital_name=form.hospital_name.data,
                contact_number=form.contact_number.data,
                notes=form.notes.data
            )
            db.session.add(request)

            # Notify admin about the new request
            admin_notification = Notification(
                user_id=1,  # Assuming admin has user_id 1
                message=f"New blood request: {form.quantity_ml.data}ml of {form.blood_type.data} blood type" + 
                        (" (Emergency)" if form.emergency.data else "")
            )
            db.session.add(admin_notification)
            db.session.commit()

            flash('Blood request submitted successfully.', 'success')
            return redirect(url_for('recipient_dashboard'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Blood request error: {str(e)}")
            flash('An error occurred while submitting your request. Please try again.', 'danger')

    return render_template('recipient/request_blood.html', form=form)

@app.route('/admin/inventory/update', methods=['GET', 'POST'])
@login_required
def update_inventory():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_dashboard'))

    form = UpdateInventoryForm()
    if form.validate_on_submit():
        inventory = BloodInventory.query.filter_by(blood_type=form.blood_type.data).first()
        if not inventory:
            inventory = BloodInventory(blood_type=form.blood_type.data, quantity_ml=0)
            db.session.add(inventory)

        if form.operation.data == 'add':
            inventory.quantity_ml += form.quantity_ml.data
        else:
            if inventory.quantity_ml < form.quantity_ml.data:
                flash('Insufficient blood quantity in inventory.', 'danger')
                return redirect(url_for('update_inventory'))
            inventory.quantity_ml -= form.quantity_ml.data

        inventory.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Inventory updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/update_inventory.html', form=form)

@app.route('/admin/request/<int:request_id>/<string:action>')
@login_required
def handle_request(request_id, action):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_dashboard'))

    blood_request = BloodRequest.query.get_or_404(request_id)
    if action == 'approve':
        inventory = BloodInventory.query.filter_by(blood_type=blood_request.blood_type).first()
        if not inventory or inventory.quantity_ml < blood_request.quantity_ml:
            flash('Insufficient blood quantity in inventory.', 'danger')
            return redirect(url_for('admin_dashboard'))

        inventory.quantity_ml -= blood_request.quantity_ml
        blood_request.status = 'approved'

        # Notify recipient
        notification = Notification(
            user_id=blood_request.recipient_id,
            message=f"Your blood request for {blood_request.quantity_ml}ml of {blood_request.blood_type} has been approved."
        )
        db.session.add(notification)

    elif action == 'reject':
        blood_request.status = 'rejected'
        notification = Notification(
            user_id=blood_request.recipient_id,
            message=f"Your blood request for {blood_request.quantity_ml}ml of {blood_request.blood_type} has been rejected."
        )
        db.session.add(notification)

    db.session.commit()
    flash(f'Request {action}d successfully.', 'success')
    return redirect(url_for('admin_dashboard'))