# app/routes/main_routes.py

from flask import Blueprint, redirect, url_for, render_template, session
from flask_login import current_user
from app.models import Route, Schedule
from datetime import datetime
from sqlalchemy.orm import joinedload  # Ensure joinedload is imported

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'visited' in session:
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            return redirect(url_for('main.home'))
    else:
        session['visited'] = True
        return render_template('welcome.html')

@bp.route('/home')
def home():
    # Fetch routes from the database
    routes_home_to_university = Route.query.filter_by(direction='home_to_university').all()
    routes_university_to_home = Route.query.filter_by(direction='university_to_home').all()
    return render_template(
        'index.html',
        routes_home_to_university=routes_home_to_university,
        routes_university_to_home=routes_university_to_home
    )

@bp.route('/schedule/<int:route_id>')
def schedule(route_id):
    # Fetch schedule for the route
    schedules = Schedule.query.filter_by(route_id=route_id).all()
    return render_template('schedule.html', schedules=schedules)

@bp.route('/live_schedule')
def live_schedule():
    # Fetch live schedules with driver information
    current_time = datetime.utcnow()
    live_schedules = Schedule.query.options(
        joinedload(Schedule.driver),
        joinedload(Schedule.bus),
        joinedload(Schedule.route)
    ).filter(
        Schedule.is_live == True,
        Schedule.live_until > current_time
    ).all()
    return render_template('live_schedule.html', live_schedules=live_schedules)

@bp.route('/live_location')
def live_location():
    # Implement live location functionality
    return render_template('live_location.html')

# Add any other routes you have
