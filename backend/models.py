from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(120), nullable=True) # User's full name
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # For admin privileges

    def __init__(self, username, password, name=None, is_admin=False):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.name = name
        self.is_admin = is_admin

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
