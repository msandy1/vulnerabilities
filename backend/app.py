import os
from flask import Flask, request, jsonify, render_template, session # Added render_template and session
from .models import db, bcrypt, User  # Import db, bcrypt, User from models.py
from .database import init_db       # Import init_db from database.py

# Determine the absolute path for the instance folder
instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24)) # Important for session management, etc.
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
# init_db(app) # Call init_db to ensure tables are created. This can also be done via a CLI command.

@app.cli.command("create-db")
def create_db_command():
    """Creates the database tables and a default admin user."""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

        # Create a default admin user if one doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_password = 'adminpassword' # Change in a real application
            admin_user = User(username='admin', password=admin_password, name='Admin User', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user 'admin' created with password '{admin_password}'.")
        else:
            print("Admin user 'admin' already exists.")

@app.route('/')
def hello():
    # A simple route to check if the app is running
    return "Hello from Flask backend!"

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    password = data.get('password')
    name = data.get('name') # Optional name field

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409 # 409 Conflict

    try:
        new_user = User(username=username, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        # Log the exception e
        print(f"Error during registration: {e}")
        return jsonify({"error": "Registration failed due to an internal error"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # For now, just return user info. Session/token management can be added later.
        return jsonify({
            "message": "Login successful",
            "user": {
                "username": user.username,
                "name": user.name,
                "is_admin": user.is_admin
            }
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Optional: Placeholder for logout if server-side sessions were used.
# For client-side (localStorage) token/info, logout is mainly a frontend task.
@app.route('/api/logout', methods=['POST']) # Or GET
def logout():
    # If using server-side sessions (e.g., Flask-Login), clear session here.
    # session.clear() # Example if using Flask session
    return jsonify({"message": "Logout action processed (if server-side sessions were used)"}), 200

# Placeholder for an endpoint that might require authentication in the future
@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    # This would typically check for a valid session token or session cookie
    # For now, it's a placeholder.
    # if 'user_id' in session: # Example if using Flask session
    #    return jsonify({"is_authenticated": True, "user_id": session['user_id']}), 200
    return jsonify({"is_authenticated": False, "message": "This is a placeholder for auth check."}), 200

# Simplified admin check - replace with proper auth
def is_user_admin():
    # This is a placeholder. In a real app, you'd check a server-side session
    # or token that confirms the logged-in user is an admin.
    # For this exercise, we will just allow access if a query param is set or similar,
    # OR we can make the admin page accessible if the default admin exists.
    # For now, let's just check if the default 'admin' user is trying to access.
    # This is NOT a login system, just a placeholder.
    # A proper admin login would set something in the session.
    # For this example, we will just allow access.
    # The delete action will have a more specific (though still simplified) check.
    # In a real app, check session['is_admin'] or similar.
    # return session.get('is_admin', False)
    return True # Placeholder for now, allowing access to /admin page route for testing.

@app.route('/admin')
def admin_page():
    # Proper admin authentication should be done here using sessions or tokens.
    # For now, this route is accessible, but actions like delete will have checks.
    # if not is_user_admin():
    #     return jsonify({"error": "Unauthorized"}), 403 # Or redirect to login

    users_list = User.query.order_by(User.id).all() # Get all users, ordered by ID
    # The messages here are for if the delete action (on this page itself) caused a redirect with a message.
    # success_message = request.args.get('success_message')
    # error_message = request.args.get('error_message')
    # For now, these messages are not implemented via query params on redirect.
    return render_template('admin.html', users=users_list, title="Admin - User Management")


@app.route('/api/admin/delete_user/<string:username>', methods=['DELETE', 'POST']) # Allow POST for simplicity from basic HTML/JS
def delete_user(username):
    # CRITICAL: Add proper admin authentication here in a real app.
    # This check is a placeholder and NOT secure.
    # It assumes that if 'admin' user exists, this action is performed by them.
    # Or, more realistically, that a frontend check + knowing the URL is "enough" for this demo.
    # A real app must verify the *current session* belongs to an admin.
    admin_user_check = User.query.filter_by(username='admin', is_admin=True).first()
    if not admin_user_check: # If default admin doesn't exist or isn't admin, something is wrong.
         return jsonify({"error": "Admin functions not available or not authorized."}), 403

    # It's better to check the actual logged-in user's admin status from a session.
    # For example: if not session.get('is_admin'): return jsonify(...), 403

    if username == 'admin': # Prevent deleting the main admin
        return jsonify({"error": "Cannot delete the primary admin account."}), 403

    user_to_delete = User.query.filter_by(username=username).first()
    if not user_to_delete:
        return jsonify({"error": "User not found."}), 404

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({"message": f"User '{username}' deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user {username}: {e}") # Log error
        return jsonify({"error": "Failed to delete user due to an internal error."}), 500

if __name__ == '__main__':
    # Ensure the app context is available for db.create_all() if run directly
    # and not using the 'flask create-db' command.
    # However, using the CLI command is cleaner for setup.
    with app.app_context():
        db.create_all() # Ensures tables are created when app runs directly, if not using CLI.
    app.run(debug=True) # Runs on port 5000 by default
