"""Flask application factory for the quiz application.

This module initializes the Flask application, configures extensions,
and registers blueprints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

# Load environment variables from .env file
load_dotenv()


def create_app():
    """Create and configure the Flask application.

    This function initializes the Flask app, configures SQLAlchemy,
    LoginManager, CSRF protection, and database migration. It also
    imports and registers blueprints for routing.

    Returns:
        Flask: The initialized Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)                # Initialize SQLAlchemy with the app
    login_manager.init_app(app)     # Initialize LoginManager with the app
    csrf.init_app(app)              # Initialize CSRF protection
    migrate.init_app(app, db)       # Initialize database migration

    # Import and register blueprints
    from .routes import main        # Import the main blueprint
    app.register_blueprint(main)    # Register the main blueprint

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()             # Create all database tables

    return app                      # Return the initialized Flask application
