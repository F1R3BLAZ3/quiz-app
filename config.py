import os


class Config:
    """
    Configuration class for setting up application-wide configurations.

    Attributes:
        SECRET_KEY (str): The secret key used for securing sessions.
        SQLALCHEMY_DATABASE_URI (str): Database URI for SQLAlchemy.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag for tracking modifications
        in SQLAlchemy.
        SESSION_TYPE (str): Specifies the type of session storage.
        CSRF_ENABLED (bool): Enables CSRF protection in the application.
        QUIZ_TIME_LIMIT (int): Time limit for quizzes, in seconds
        (default is 20 minutes).
    """

    # Secret key for securing user sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

    # Database URI for SQLAlchemy (defaults to a local SQLite database
    # if not provided)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')

    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configure session type (filesystem for local storage)
    SESSION_TYPE = 'filesystem'

    # Enable CSRF protection across the app
    CSRF_ENABLED = True

    # Set a time limit for quizzes (in seconds, here it's 20 minutes)
    QUIZ_TIME_LIMIT = 20 * 60
