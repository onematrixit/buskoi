# app/routes/admin_routes.py

import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app
)
from flask_login import login_required, current_user
from app.models import User, Driver, Bus, Schedule, Route, db
from app.forms import (
    LiveScheduleForm, UserForm, DriverForm, BusForm,
    RouteForm, ScheduleForm, AddUserForm, DeleteForm
)
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

bp = Blueprint('admin', __name__)

# Ensure that only admins can access these routes
@bp.before_request
@login_required
def before_request():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.home'))

# Admin Dashboard
@bp.route('/dashboard')
def dashboard():
    """
    Display the admin dashboard with overview statistics.
    """
    # Retrieve all necessary data with eager loading to optimize queries
    buses = Bus.query.all()
    drivers = Driver.query.all()
    routes = Route.query.all()
    users = User.query.filter_by(is_admin=False).all()
    admins = User.query.filter_by(is_admin=True).all()
    live_schedules = Schedule.query.filter_by(is_live=True).all()

    # Calculate counts
    total_buses = len(buses)
    total_routes = len(routes)
    total_drivers = len(drivers)
    total_users = len(users)
    total_admins = len(admins)
    total_live_schedules = len(live_schedules)

    return render_template(
        'admin/dashboard.html',
        total_buses=total_buses,
        total_routes=total_routes,
        total_drivers=total_drivers,
        total_users=total_users,
        total_admins=total_admins,
        total_live_schedules=total_live_schedules,
        buses=buses,
        drivers=drivers,
        routes=routes,
        users=users,
        admins=admins,
        live_schedules=live_schedules
    )

# Manage Users
@bp.route('/users')
def manage_users():
    """
    Display a list of all non-admin users.
    """
    users = User.query.filter_by(is_admin=False).all()
    delete_form = DeleteForm()  # Instantiate DeleteForm
    return render_template('admin/manage_users.html', users=users, delete_form=delete_form)

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """
    Edit an existing user's details.
    """
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)  # Pass existing user data to the form

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.is_admin = form.is_admin.data

        # Handle profile picture upload
        if form.profile_pic.data:
            pic_filename = secure_filename(form.profile_pic.data.filename)
            pic_path = os.path.join(current_app.root_path, 'static/profile_pics', pic_filename)
            form.profile_pic.data.save(pic_path)
            user.profile_pic = pic_filename  # Update the user's profile_pic field

        # Optionally update the password if provided
        if form.password.data:
            user.set_password(form.password.data)

        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
        except IntegrityError:
            db.session.rollback()  # Handle unique constraint errors or other DB issues
            flash('An error occurred. Please try again.', 'danger')

    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Delete a user.
    """
    form = DeleteForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            flash('User has been deleted!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the user: {str(e)}', 'danger')
    else:
        flash('Invalid delete request.', 'danger')
    return redirect(url_for('admin.manage_users'))  # Redirect back to the manage users page

@bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Add a new user.
    """
    form = AddUserForm()

    if form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.add_user'))  # Redirect back to the add user page

        # Create a new user from form data
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            is_admin=form.is_admin.data
        )

        # Use the set_password method to hash the password
        new_user.set_password(form.password.data)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!', 'success')

        # Redirect to users page after adding the user
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html', form=form)

# Manage Drivers
@bp.route('/drivers')
def manage_drivers():
    """
    Display a list of all drivers.
    """
    drivers = Driver.query.all()
    delete_form = DeleteForm()
    return render_template('admin/manage_drivers.html', drivers=drivers, delete_form=delete_form)

@bp.route('/drivers/add', methods=['GET', 'POST'])
def add_driver():
    """
    Add a new driver.
    """
    form = DriverForm()
    # Populate SelectField choices dynamically
    form.route_id.choices = [(route.id, route.name) for route in Route.query.all()]
    form.bus_id.choices = [(bus.id, f"{bus.bus_number} - {bus.model}") for bus in Bus.query.all()]
    if form.validate_on_submit():
        driver = Driver(
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            route_id=form.route_id.data,
            bus_id=form.bus_id.data
        )
        db.session.add(driver)
        db.session.commit()
        flash('Driver added successfully.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('admin/add_driver.html', form=form)

@bp.route('/drivers/edit/<int:driver_id>', methods=['GET', 'POST'])
def edit_driver(driver_id):
    """
    Edit an existing driver's details.
    """
    driver = Driver.query.get_or_404(driver_id)
    form = DriverForm(obj=driver)
    # Populate SelectField choices dynamically
    form.route_id.choices = [(route.id, route.name) for route in Route.query.all()]
    form.bus_id.choices = [(bus.id, f"{bus.bus_number} - {bus.model}") for bus in Bus.query.all()]
    if form.validate_on_submit():
        driver.name = form.name.data
        driver.phone = form.phone.data
        driver.address = form.address.data
        driver.route_id = form.route_id.data
        driver.bus_id = form.bus_id.data
        db.session.commit()
        flash('Driver updated successfully.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('admin/edit_driver.html', form=form, driver=driver)

@bp.route('/drivers/delete/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    """
    Delete a driver.
    """
    form = DeleteForm()
    if form.validate_on_submit():
        driver = Driver.query.get_or_404(driver_id)
        try:
            db.session.delete(driver)
            db.session.commit()
            flash('Driver has been deleted!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the driver: {str(e)}', 'danger')
    else:
        flash('Invalid delete request.', 'danger')
    return redirect(url_for('admin.manage_drivers'))

# Manage Buses
@bp.route('/buses')
def manage_buses():
    """
    Display a list of all buses.
    """
    buses = Bus.query.all()
    delete_form = DeleteForm()
    return render_template('admin/manage_buses.html', buses=buses, delete_form=delete_form)

@bp.route('/buses/add', methods=['GET', 'POST'])
def add_bus():
    """
    Add a new bus.
    """
    form = BusForm()
    if form.validate_on_submit():
        bus = Bus(
            bus_number=form.bus_number.data,
            model=form.model.data
        )
        db.session.add(bus)
        db.session.commit()
        flash('Bus added successfully.', 'success')
        return redirect(url_for('admin.manage_buses'))
    return render_template('admin/add_bus.html', form=form)

@bp.route('/buses/edit/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    """
    Edit an existing bus's details.
    """
    bus = Bus.query.get_or_404(bus_id)
    form = BusForm(obj=bus)
    if form.validate_on_submit():
        bus.bus_number = form.bus_number.data
        bus.model = form.model.data
        db.session.commit()
        flash('Bus updated successfully.', 'success')
        return redirect(url_for('admin.manage_buses'))
    return render_template('admin/edit_bus.html', form=form, bus=bus)

@bp.route('/buses/delete/<int:bus_id>', methods=['POST'])
def delete_bus(bus_id):
    """
    Delete a bus.
    """
    form = DeleteForm()
    if form.validate_on_submit():
        bus = Bus.query.get_or_404(bus_id)
        try:
            db.session.delete(bus)
            db.session.commit()
            flash('Bus has been deleted!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the bus: {str(e)}', 'danger')
    else:
        flash('Invalid delete request.', 'danger')
    return redirect(url_for('admin.manage_buses'))

# Manage Routes
@bp.route('/routes')
def manage_routes():
    """
    Display a list of all routes.
    """
    routes = Route.query.all()
    delete_form = DeleteForm()  # Instantiate DeleteForm
    return render_template('admin/manage_routes.html', routes=routes, delete_form=delete_form)

@bp.route('/routes/add', methods=['GET', 'POST'])
def add_route():
    """
    Add a new route.
    """
    form = RouteForm()
    if form.validate_on_submit():
        route = Route(
            name=form.name.data,
            map_data=form.map_data.data,
            direction=form.direction.data
        )
        db.session.add(route)
        db.session.commit()
        flash('Route added successfully.', 'success')
        return redirect(url_for('admin.manage_routes'))
    return render_template('admin/add_route.html', form=form)

@bp.route('/routes/edit/<int:route_id>', methods=['GET', 'POST'])
def edit_route(route_id):
    """
    Edit an existing route's details.
    """
    route = Route.query.get_or_404(route_id)
    form = RouteForm(obj=route)
    if form.validate_on_submit():
        route.name = form.name.data
        route.map_data = form.map_data.data
        route.direction = form.direction.data
        db.session.commit()
        flash('Route updated successfully.', 'success')
        return redirect(url_for('admin.manage_routes'))
    return render_template('admin/edit_route.html', form=form, route=route)

@bp.route('/routes/delete/<int:route_id>', methods=['POST'])
def delete_route(route_id):
    """
    Delete a route.
    """
    form = DeleteForm()
    if form.validate_on_submit():
        route = Route.query.get_or_404(route_id)
        try:
            db.session.delete(route)
            db.session.commit()
            flash('Route has been deleted!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the route: {str(e)}', 'danger')
    else:
        flash('Invalid delete request.', 'danger')
    return redirect(url_for('admin.manage_routes'))

# Manage Schedules
@bp.route('/schedules')
def manage_schedules():
    """
    Display a list of all schedules.
    """
    schedules = Schedule.query.options(
        joinedload(Schedule.driver),
        joinedload(Schedule.bus),
        joinedload(Schedule.route)
    ).all()
    delete_form = DeleteForm()  # Instantiate DeleteForm
    return render_template('admin/manage_schedules.html', schedules=schedules, delete_form=delete_form)

@bp.route('/schedules/add', methods=['GET', 'POST'])
def add_schedule():
    """
    Add a new schedule.
    """
    form = ScheduleForm()
    # Populate SelectField choices dynamically
    form.bus_id.choices = [(bus.id, f"{bus.bus_number} - {bus.model}") for bus in Bus.query.all()]
    form.route_id.choices = [(route.id, route.name) for route in Route.query.all()]
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]  # Populate driver choices

    if form.validate_on_submit():
        try:
            bus_id = form.bus_id.data
            route_id = form.route_id.data
            driver_id = form.driver_id.data
            departure_time = form.departure_time.data
            is_live = form.is_live.data
            live_duration = form.live_duration.data if form.live_duration.data else 0

            live_until = departure_time + timedelta(minutes=live_duration) if is_live else None

            schedule = Schedule(
                bus_id=bus_id,
                route_id=route_id,
                driver_id=driver_id,  # Assign driver
                departure_time=departure_time,
                is_live=is_live,
                live_until=live_until
            )
            db.session.add(schedule)
            db.session.commit()

            flash('Schedule added successfully.', 'success')
            return redirect(url_for('admin.manage_schedules'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while adding the schedule: {str(e)}', 'danger')
            return render_template('admin/add_schedule.html', form=form)
    else:
        # Optional: Log form errors for debugging
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('admin/add_schedule.html', form=form)

@bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    """
    Edit an existing schedule's details.
    """
    schedule = Schedule.query.get_or_404(schedule_id)
    form = ScheduleForm(obj=schedule)

    # Populate SelectField choices dynamically
    form.bus_id.choices = [(bus.id, f"{bus.bus_number} - {bus.model}") for bus in Bus.query.all()]
    form.route_id.choices = [(route.id, route.name) for route in Route.query.all()]
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]  # Populate driver choices

    if form.validate_on_submit():
        try:
            # Update schedule details
            schedule.bus_id = form.bus_id.data
            schedule.route_id = form.route_id.data
            schedule.driver_id = form.driver_id.data  # Update driver
            schedule.departure_time = form.departure_time.data
            schedule.is_live = form.is_live.data
            live_duration = form.live_duration.data if form.live_duration.data else 0
            schedule.live_until = schedule.departure_time + timedelta(minutes=live_duration) if form.is_live.data else None

            db.session.commit()
            flash('Schedule updated successfully.', 'success')
            return redirect(url_for('admin.manage_schedules'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the schedule: {str(e)}', 'danger')
            return render_template('admin/edit_schedule.html', form=form, schedule=schedule)
    else:
        # Pre-populate form fields with existing data
        if request.method == 'GET':
            form.departure_time.data = schedule.departure_time.strftime('%Y-%m-%dT%H:%M')
            form.live_duration.data = schedule.live_until.strftime('%Y-%m-%dT%H:%M') if schedule.live_until else ''

        # Optional: Log form errors for debugging
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('admin/edit_schedule.html', form=form, schedule=schedule)

@bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    """
    Delete a schedule.
    """
    form = DeleteForm()
    if form.validate_on_submit():
        schedule = Schedule.query.get_or_404(schedule_id)
        try:
            db.session.delete(schedule)
            db.session.commit()
            flash('Schedule deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the schedule: {str(e)}', 'danger')
    else:
        flash('Invalid delete request.', 'danger')
    return redirect(url_for('admin.manage_schedules'))

# Create Live Schedule
@bp.route('/create_live_schedule', methods=['GET', 'POST'])
def create_live_schedule():
    """
    Create a new live schedule.
    """
    form = LiveScheduleForm()
    # Populate SelectField choices dynamically
    form.bus_id.choices = [(bus.id, f"{bus.bus_number} - {bus.model}") for bus in Bus.query.all()]
    form.route_id.choices = [(route.id, route.name) for route in Route.query.all()]
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]  # Populate driver choices

    if form.validate_on_submit():
        try:
            bus_id = form.bus_id.data
            route_id = form.route_id.data
            driver_id = form.driver_id.data
            live_duration = form.live_duration.data
            live_until = datetime.utcnow() + timedelta(minutes=live_duration)

            schedule = Schedule(
                bus_id=bus_id,
                route_id=route_id,
                driver_id=driver_id,
                departure_time=datetime.utcnow(),
                is_live=True,
                live_until=live_until
            )
            db.session.add(schedule)
            db.session.commit()
            flash('Live schedule created successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating the live schedule: {str(e)}', 'danger')
            return render_template('admin/create_live_schedule.html', form=form)

    else:
        # Optional: Log form errors for debugging
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('admin/create_live_schedule.html', form=form)

# Admin Profile
@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    Admin user profile page for updating personal details.
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
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html', form=form)

# Admin Settings
@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Admin settings page.
    """
    if not current_user.is_admin:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('main.home'))

    # Add any settings-related functionality here

    return render_template('admin/settings.html')
