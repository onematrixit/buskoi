from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    from .routes import admin_routes, user_routes, auth_routes
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(auth_routes.bp)

    return app
