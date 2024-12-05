# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Ensure you have a config.py with Config class

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set the login view for @login_required
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register Blueprints
    from app.routes.main_routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.admin_routes import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.user_routes import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp)  # Removed url_prefix='/auth' to allow routes like '/login'

    # Register CLI commands
    from app.scripts.assign_drivers import assign_drivers
    app.cli.add_command(assign_drivers)

    return app
