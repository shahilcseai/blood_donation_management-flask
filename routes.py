from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, DonorProfile, BloodInventory, BloodRequest, Notification, DonationSchedule #Added DonationSchedule
from forms import LoginForm, RegistrationForm, DonorProfileForm, BloodRequestForm, InventoryUpdateForm, DonationScheduleForm, DonorSearchForm #Added DonationScheduleForm, DonorSearchForm
from datetime import datetime
from sqlalchemy import inspect

def init_blood_inventory():
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    for blood_type in blood_types:
        if not BloodInventory.query.filter_by(blood_type=blood_type).first():
            inventory = BloodInventory(blood_type=blood_type, quantity_ml=0)
            db.session.add(inventory)
    db.session.commit()

@app.route('/')
def home():
    # Initialize blood inventory if empty
    if not BloodInventory.query.first():
        init_blood_inventory()
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
            if user.role == 'donor':
                return redirect(next_page or url_for('donor_dashboard'))
            elif user.role == 'recipient':
                return redirect(next_page or url_for('recipient_dashboard'))
            else:
                return redirect(next_page or url_for('admin_dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/donor/dashboard')
@login_required
def donor_dashboard():
    if current_user.role != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    profile = current_user.donor_profile
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    health_records = []  # To be implemented
    return render_template('donor/dashboard.html', profile=profile, notifications=notifications, health_records=health_records)

@app.route('/donor/create_profile', methods=['GET', 'POST'])
@login_required
def create_donor_profile():
    if current_user.role != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    if current_user.donor_profile:
        return redirect(url_for('donor_dashboard'))

    form = DonorProfileForm()
    if form.validate_on_submit():
        profile = DonorProfile(
            user_id=current_user.id,
            blood_type=form.blood_type.data,
            last_donation=form.last_donation.data,
            medical_conditions=form.medical_conditions.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            # Initialize these as None for now, can be updated later with geocoding
            latitude=None,
            longitude=None,
            availability_status='available'
        )
        db.session.add(profile)
        try:
            db.session.commit()
            flash('Donor profile created successfully!', 'success')
            return redirect(url_for('donor_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating profile. Please try again.', 'danger')
            app.logger.error(f"Error creating donor profile: {str(e)}")

    return render_template('donor/create_profile.html', form=form)

@app.route('/recipient/dashboard')
@login_required
def recipient_dashboard():
    if current_user.role != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    requests = BloodRequest.query.filter_by(recipient_id=current_user.id).order_by(BloodRequest.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('recipient/dashboard.html', requests=requests, notifications=notifications)

@app.route('/recipient/request_blood', methods=['GET', 'POST'])
@login_required
def request_blood():
    if current_user.role != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    form = BloodRequestForm()
    if form.validate_on_submit():
        request = BloodRequest(
            recipient_id=current_user.id,
            blood_type=form.blood_type.data,
            quantity_ml=form.quantity_ml.data,
            hospital_name=form.hospital_name.data,
            contact_number=form.contact_number.data,
            emergency=form.emergency.data,
            notes=form.notes.data
        )
        db.session.add(request)
        db.session.commit()
        flash('Blood request submitted successfully!', 'success')
        return redirect(url_for('recipient_dashboard'))
    return render_template('recipient/request_blood.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    inventory = BloodInventory.query.all()
    requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    users = User.query.all()
    return render_template('admin/dashboard.html', inventory=inventory, requests=requests, users=users)

@app.route('/admin/update_inventory', methods=['GET', 'POST'])
@login_required
def update_inventory():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    form = InventoryUpdateForm()
    inventory = BloodInventory.query.all()
    
    if form.validate_on_submit():
        blood_type = form.blood_type.data
        quantity = form.quantity_ml.data
        operation = form.operation.data
        
        inventory_item = BloodInventory.query.filter_by(blood_type=blood_type).first()
        if not inventory_item:
            inventory_item = BloodInventory(blood_type=blood_type, quantity_ml=0)
            db.session.add(inventory_item)
        
        if operation == 'add':
            inventory_item.quantity_ml += quantity
        else:
            if inventory_item.quantity_ml >= quantity:
                inventory_item.quantity_ml -= quantity
            else:
                flash('Insufficient inventory for the requested quantity.', 'danger')
                return redirect(url_for('update_inventory'))
        
        inventory_item.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Inventory updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/update_inventory.html', form=form, inventory=inventory)

@app.route('/admin/handle_request/<int:request_id>/<action>')
@login_required
def handle_request(request_id, action):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    blood_request = BloodRequest.query.get_or_404(request_id)
    if action == 'approve':
        blood_request.status = 'approved'
        notification = Notification(
            user_id=blood_request.recipient_id,
            message=f'Your blood request for {blood_request.quantity_ml}ml of {blood_request.blood_type} has been approved.'
        )
        db.session.add(notification)
    elif action == 'reject':
        blood_request.status = 'rejected'
        notification = Notification(
            user_id=blood_request.recipient_id,
            message=f'Your blood request for {blood_request.quantity_ml}ml of {blood_request.blood_type} has been rejected.'
        )
        db.session.add(notification)
    
    db.session.commit()
    flash('Request has been processed.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/donor/schedule_donation', methods=['GET', 'POST'])
@login_required
def schedule_donation():
    if current_user.role != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    if not current_user.donor_profile:
        flash('Please create your donor profile first.', 'warning')
        return redirect(url_for('create_donor_profile'))

    form = DonationScheduleForm()
    if form.validate_on_submit():
        scheduled_date = form.donation_date.data

        # Convert last_donation datetime to date for comparison
        last_donation = current_user.donor_profile.last_donation
        if last_donation:
            last_donation_date = last_donation.date() if isinstance(last_donation, datetime) else last_donation
            days_difference = (scheduled_date - last_donation_date).days
            if days_difference < 56:
                flash('You must wait at least 56 days between donations.', 'danger')
                return redirect(url_for('schedule_donation'))

        donation = DonationSchedule(
            donor_id=current_user.id,
            scheduled_date=datetime.combine(scheduled_date, datetime.min.time()),
            status='scheduled'
        )
        db.session.add(donation)

        # Update donor profile with datetime object
        current_user.donor_profile.last_donation = datetime.combine(scheduled_date, datetime.min.time())
        current_user.donor_profile.total_donations += 1

        db.session.commit()
        flash('Donation scheduled successfully!', 'success')
        return redirect(url_for('donor_dashboard'))

    return render_template('donor/schedule_donation.html', form=form, today=datetime.now().date())

@app.route('/learn/donation')
def learn_about_donation():
    return render_template('learn/about_donation.html')

@app.route('/learn/process')
def donation_process():
    return render_template('learn/donation_process.html')

@app.context_processor
def utility_processor():
    def get_notifications():
        if current_user.is_authenticated:
            return Notification.query.filter_by(user_id=current_user.id, read=False).all()
        return []
    return dict(notifications=get_notifications())

@app.route('/donor/search', methods=['GET'])
def search_donors():
    form = DonorSearchForm()
    donors = []

    if any([request.args.get('blood_type'), request.args.get('city'),
            request.args.get('state'), request.args.get('zip_code')]):
        query = DonorProfile.query.join(User)

        if request.args.get('blood_type'):
            query = query.filter(DonorProfile.blood_type == request.args.get('blood_type'))

        if request.args.get('city'):
            query = query.filter(DonorProfile.city.ilike(f"%{request.args.get('city')}%"))

        if request.args.get('state'):
            query = query.filter(DonorProfile.state.ilike(f"%{request.args.get('state')}%"))

        if request.args.get('zip_code'):
            query = query.filter(DonorProfile.zip_code == request.args.get('zip_code'))

        donors = query.all()

    return render_template('donor/search.html', form=form, donors=donors)

@app.route('/learn/eligibility')
def eligibility_requirements():
    return render_template('learn/eligibility.html')