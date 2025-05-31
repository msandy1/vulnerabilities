# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by some Python packages
# RUN apt-get update && apt-get install -y --no-install-recommends some-build-tools gcc

# Copy requirements file first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ /app/backend/

# Copy the static frontend files
# These files (HTML, CSS, JS) will be served by Flask in this setup,
# or could be served by a separate web server like Nginx in a more complex setup.
COPY index.html .
COPY login.html .
COPY registration.html .
COPY account.html .
# If there are any CSS or JS static assets directly in the root or a static/css/js folder, copy them too.
# For example, if you have a 'static' folder for general assets (not the Flask one):
# COPY static/ /app/static/

# Ensure the instance folder for SQLite exists (though app.py also tries to create it)
RUN mkdir -p /app/backend/instance

# Expose the port the app runs on (Flask default is 5000)
EXPOSE 5000

# Define the command to run the application
# This will first run the database creation/admin user setup, then start Flask.
# Note: For production, use a proper WSGI server like Gunicorn instead of Flask's dev server.
CMD ["sh", "-c", "flask --app backend.app create-db && flask --app backend.app run --host=0.0.0.0 --port=5000"]
