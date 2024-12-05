# app/routes/user_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models import Schedule, Route, Driver, db
from app.forms import UserForm
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload  # Import joinedload
from sqlalchemy.exc import IntegrityError  # Import IntegrityError for error handling
import os  # Import os for file path operations

bp = Blueprint('user', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard displaying available routes and schedules.
    """
    routes = Route.query.all()
    return render_template('user/dashboard.html', user=current_user, routes=routes)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile page for updating personal details.
    """
    form = UserForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        if form.password.data:
            current_user.set_password(form.password.data)
        # Handle profile picture upload
        if form.profile_pic.data:
            pic_filename = secure_filename(form.profile_pic.data.filename)
            pic_path = os.path.join(current_app.root_path, 'static/profile_pics', pic_filename)
            form.profile_pic.data.save(pic_path)
            current_user.profile_pic = pic_filename  # Update the user's profile_pic field
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('user.profile'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    return render_template('user/profile.html', form=form)

@bp.route('/route/<int:route_id>/schedules')
def route_schedules(route_id):
    """
    Display schedules for a specific route.
    """
    route = Route.query.get_or_404(route_id)
    schedules = Schedule.query.filter_by(route_id=route_id, is_live=False).order_by(Schedule.departure_time).all()
    return render_template('user/route_schedules.html', route=route, schedules=schedules)

@bp.route('/live_schedules')
@login_required
def live_schedules():
    """
    Display all live schedules.
    """
    current_time = datetime.utcnow()
    schedules = Schedule.query.filter(
        Schedule.is_live == True,
        Schedule.live_until >= current_time
    ).options(
        joinedload(Schedule.driver),
        joinedload(Schedule.bus),
        joinedload(Schedule.route)
    ).all()
    return render_template('user/live_schedules.html', schedules=schedules)

@bp.route('/live_location')
@login_required
def live_location():
    """
    Live location tracking for buses.
    """
    # Implement live location tracking logic here
    return render_template('user/live_location.html')

@bp.route('/request_delay/<int:schedule_id>', methods=['POST'])
@login_required
def request_delay(schedule_id):
    """
    Allow users to request a delay for a specific schedule.
    """
    schedule = Schedule.query.get_or_404(schedule_id)
    # Implement delay request logic (e.g., updating schedule status, notifying admin)
    # For now, we'll just flash a message
    flash('Delay request sent.', 'info')
    return redirect(url_for('user.dashboard'))

@bp.route('/call_driver/<int:driver_id>')
@login_required
def call_driver(driver_id):
    """
    Provide a way for users to contact the driver.
    """
    driver = Driver.query.get_or_404(driver_id)
    # Implement contact logic (e.g., send email, initiate call via integrated service)
    # For now, we'll just render a contact page
    return render_template('user/call_driver.html', driver=driver)
