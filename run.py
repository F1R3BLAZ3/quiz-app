"""
Entry point for running the Flask application.

This module imports and initializes the Flask application using the
application factory pattern, allowing the app to be run as a standalone script.
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
