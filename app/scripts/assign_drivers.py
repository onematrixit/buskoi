# app/scripts/assign_drivers.py

import click
from flask.cli import with_appcontext
from app import db
from app.models import Schedule, Driver

@click.command('assign-drivers')
@with_appcontext
def assign_drivers():
    """
    Assigns a default driver to all schedules that currently have no driver assigned.
    """
    default_driver = Driver.query.first()
    if not default_driver:
        click.echo("No drivers available to assign.")
        return

    schedules = Schedule.query.filter_by(driver_id=None).all()
    if not schedules:
        click.echo("No schedules need driver assignments.")
        return

    for schedule in schedules:
        schedule.driver_id = default_driver.id
        click.echo(f"Assigned Driver {default_driver.name} to Schedule ID {schedule.id}")

    try:
        db.session.commit()
        click.echo("Driver assignment completed.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"An error occurred during driver assignment: {str(e)}")
