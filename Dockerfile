# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app
ENV PORT 8000
# DJANGO_SETTINGS_MODULE will be implicitly config.settings due to project structure and CWD.

WORKDIR $APP_HOME

# Install system dependencies (if any - e.g., for psycopg2 if not using -binary)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# Our Django project 'config' is at the root of the repo (/app in WORKDIR)
# manage.py is directly in /app (moved from /app/config/ in a previous step if I recall, or created there)
# Let's verify manage.py location first.
# Assuming manage.py is at $APP_HOME/manage.py (which is /app/manage.py)
# And the project directory 'config' (with settings.py, wsgi.py, etc.) is at $APP_HOME/config/
COPY manage.py $APP_HOME/
COPY config/ $APP_HOME/config/

# The .env file contains environment variables for settings
COPY .env $APP_HOME/.env

# Expose the port the app runs on
EXPOSE $PORT

# Define the command to run the application
# Create a simple startup script to handle this.
COPY <<END_SCRIPT entrypoint.sh
#!/bin/sh
# Exit on error
set -e

echo "Running Django database migrations..."
# manage.py is at the WORKDIR root /app
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
# Gunicorn should bind to 0.0.0.0 to be accessible from outside the container.
# The number of workers can be tuned. (2 * NUM_CORES) + 1 is a common recommendation.
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:\${PORT}" \
    --workers 3 \
    --log-level=info \
    --access-logfile '-' \
    --error-logfile '-'

END_SCRIPT
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
