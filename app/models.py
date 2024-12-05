# app/models.py

from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Plural for consistency
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(256), nullable=True)  # File path for profile picture
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """
        Hash and set the user's password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the user's password against the hashed version.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Route(db.Model):
    __tablename__ = 'routes'  # Plural for consistency
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    map_data = db.Column(db.Text, nullable=False)  # JSON data for Google Maps
    direction = db.Column(db.String(50), nullable=False)  # e.g., 'home_to_university'

    drivers = db.relationship('Driver', back_populates='route', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='route', lazy='dynamic')

    def __repr__(self):
        return f'<Route {self.name}>'

class Bus(db.Model):
    __tablename__ = 'buses'  # Plural for consistency
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='available')  # e.g., 'available', 'in_service'

    drivers = db.relationship('Driver', back_populates='bus', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='bus', lazy='dynamic')

    def __repr__(self):
        return f'<Bus {self.bus_number} - {self.model}>'

class Driver(db.Model):
    __tablename__ = 'drivers'  # Plural for consistency
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=True)

    bus = db.relationship('Bus', back_populates='drivers')
    route = db.relationship('Route', back_populates='drivers')
    schedules = db.relationship('Schedule', back_populates='driver', lazy='dynamic')  # Added relationship

    def __repr__(self):
        return f'<Driver {self.name}>'

class Schedule(db.Model):
    __tablename__ = 'schedules'  # Plural for consistency
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)  # Added driver_id
    departure_time = db.Column(db.DateTime, nullable=False)
    is_live = db.Column(db.Boolean, default=False)
    live_until = db.Column(db.DateTime)
    is_disabled = db.Column(db.Boolean, default=False)

    # Relationships
    bus = db.relationship('Bus', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')
    driver = db.relationship('Driver', back_populates='schedules')  # Added relationship

    def time_remaining(self):
        """
        Calculate time remaining for a live schedule.
        """
        if self.live_until:
            return max(0, (self.live_until - datetime.utcnow()).total_seconds())
        return 0

    def __repr__(self):
        return f'<Schedule Bus: {self.bus.bus_number}, Route: {self.route.name if self.route else "N/A"}, Driver: {self.driver.name}>'
