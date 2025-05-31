from flask_sqlalchemy import SQLAlchemy
# Correctly import db from the local models.py.
# Assuming models.py is in the same directory (backend), this import is fine.
from .models import db

# This file can be expanded later if needed for more complex db operations or setup.
# For now, its main role is to ensure db from models is accessible for app initialization.

def init_db(app):
    """Initializes the database and creates tables if they don't exist."""
    db.init_app(app) # Initialize db with the Flask app context
    with app.app_context():
        db.create_all()
        print("Database tables created (if they didn't exist).")
