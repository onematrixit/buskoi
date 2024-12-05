# app/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    FileField, StringField, PasswordField, SubmitField,
    BooleanField, SelectField, TextAreaField, IntegerField
)
from wtforms.validators import (
    DataRequired, Email, Length, Optional, NumberRange,
    ValidationError
)
from wtforms_components import DateTimeLocalField  # Import DateTimeLocalField
from flask_wtf.file import FileAllowed, FileRequired  # Import necessary validators

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password')  # Optional: Password update
    is_admin = BooleanField('Is Admin')
    profile_pic = FileField(
        'Update Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')]
    )
    submit = SubmitField('Submit')

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Add User')

class DriverForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(max=128)])
    route_id = SelectField('Route', coerce=int, validators=[DataRequired()])
    bus_id = SelectField('Bus', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class BusForm(FlaskForm):
    bus_number = StringField('Bus Number', validators=[DataRequired(), Length(max=20)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Add Bus')

class RouteForm(FlaskForm):
    name = StringField('Route Name', validators=[DataRequired(), Length(max=128)])
    map_data = TextAreaField('Map Data (JSON)', validators=[DataRequired()])
    direction = StringField('Direction', validators=[DataRequired(), Length(max=50)])  # e.g., 'home_to_university'
    submit = SubmitField('Submit')

class ScheduleForm(FlaskForm):
    bus_id = SelectField('Bus', coerce=int, validators=[DataRequired()])
    route_id = SelectField('Route', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('Driver', coerce=int, validators=[DataRequired()])  # Added driver selection
    departure_time = DateTimeLocalField(
        'Departure Time',
        format='%Y-%m-%dT%H:%M',  # Matches 'datetime-local' input format
        validators=[DataRequired()]
    )
    is_live = BooleanField('Is Live Schedule')
    live_duration = IntegerField(
        'Live Duration (minutes)',
        validators=[Optional(), NumberRange(min=1, message="Duration must be at least 1 minute.")]
    )
    submit = SubmitField('Add Schedule')

# New Form: LiveScheduleForm
class LiveScheduleForm(FlaskForm):
    bus_id = SelectField('Bus', coerce=int, validators=[DataRequired()])
    route_id = SelectField('Route', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('Driver', coerce=int, validators=[DataRequired()])  # Added driver selection
    live_duration = IntegerField(
        'Live Duration (minutes)',
        validators=[DataRequired(), NumberRange(min=1, message="Duration must be at least 1 minute.")]
    )
    submit = SubmitField('Create Live Schedule')

# New Form: DeleteForm
class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
