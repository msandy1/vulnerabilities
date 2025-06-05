import sqlite3
import os
from django.core.management.base import BaseCommand
from django.conf import settings
# Adjust the import path for your User model if necessary.
# If AUTH_USER_MODEL is 'accounts.User', this is correct.
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

User = get_user_model()

# Path to the old Flask SQLite database
# The Dockerfile copies 'backend/' to '/app/backend/'
# and the original DB was 'backend/instance/users.db'
OLD_DB_PATH_INSIDE_CONTAINER = '/app/backend/instance/users.db'
# Fallback for local development if backend/instance/users.db exists relative to manage.py
# manage.py is at /app/manage.py, so settings.BASE_DIR is /app
# The old db would be at /app/backend/instance/users.db
OLD_DB_PATH_LOCAL_DEV = os.path.join(settings.BASE_DIR, 'backend', 'instance', 'users.db')


class Command(BaseCommand):
    help = 'Migrates users from the old Flask SQLite database to the new Django database.'

    def handle(self, *args, **options):
        old_db_actual_path = None
        if os.path.exists(OLD_DB_PATH_INSIDE_CONTAINER):
            old_db_actual_path = OLD_DB_PATH_INSIDE_CONTAINER
            self.stdout.write(self.style.SUCCESS(f'Found old database at: {old_db_actual_path}'))
        elif os.path.exists(OLD_DB_PATH_LOCAL_DEV):
            old_db_actual_path = OLD_DB_PATH_LOCAL_DEV
            self.stdout.write(self.style.SUCCESS(f'Found old database at: {old_db_actual_path} (local dev path)'))
        else:
            self.stderr.write(self.style.ERROR(
                f'Old database not found at {OLD_DB_PATH_INSIDE_CONTAINER} or {OLD_DB_PATH_LOCAL_DEV}. '
                'Ensure the file exists and the path is correct.'
            ))
            return

        conn = None
        try:
            conn = sqlite3.connect(old_db_actual_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, password_hash, name, registered_on, is_admin FROM users')

            flask_users_migrated = 0
            flask_users_skipped = 0

            for row in cursor.fetchall():
                flask_id, username, password_hash, name, registered_on_str, is_admin_bool = row

                # Convert registered_on from string to datetime object
                # Assuming the format in Flask DB is UTC 'YYYY-MM-DD HH:MM:SS.ffffff' or similar
                try:
                    if isinstance(registered_on_str, str):
                        # Attempt to parse with microseconds, then without if it fails
                        try:
                            registered_on_dt = datetime.datetime.strptime(registered_on_str, '%Y-%m-%d %H:%M:%S.%f')
                        except ValueError:
                            registered_on_dt = datetime.datetime.strptime(registered_on_str, '%Y-%m-%d %H:%M:%S')
                        registered_on_aware = timezone.make_aware(registered_on_dt, datetime.timezone.utc)
                    elif isinstance(registered_on_str, (int, float)): # Handle timestamp if stored as epoch
                         registered_on_dt = datetime.datetime.utcfromtimestamp(registered_on_str)
                         registered_on_aware = timezone.make_aware(registered_on_dt, datetime.timezone.utc)
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipping user {username} due to unrecognized registered_on format: {registered_on_str}'))
                        flask_users_skipped +=1
                        continue
                except ValueError as e:
                    self.stdout.write(self.style.WARNING(f'Skipping user {username} due to date parsing error for registered_on="{registered_on_str}": {e}'))
                    flask_users_skipped +=1
                    continue

                try:
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping.'))
                        flask_users_skipped += 1
                        continue

                    django_user = User()
                    django_user.username = username
                    # Directly set the password hash. Django will use BCryptSHA256PasswordHasher.
                    django_user.password = password_hash
                    django_user.name = name if name else ''

                    # Ensure date_joined and registered_on are correctly set
                    django_user.date_joined = registered_on_aware # Django's default field
                    django_user.registered_on = registered_on_aware # Custom field

                    if is_admin_bool:
                        django_user.is_staff = True
                        django_user.is_superuser = True
                    else:
                        django_user.is_staff = False
                        django_user.is_superuser = False

                    # Set a default email if necessary, or handle if it's part of Flask model
                    if not django_user.email:
                         django_user.email = f"{username}@example.com" # Placeholder email

                    # Save the user, bypassing hashing by using create_user=False logic
                    # However, direct assignment to .password and then .save() is the way for pre-hashed passwords
                    django_user.save()

                    flask_users_migrated += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated user: {username} (Flask ID: {flask_id})'))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error migrating user {username} (Flask ID: {flask_id}): {e}'))
                    flask_users_skipped += 1

            self.stdout.write(self.style.SUCCESS(f'--- Migration Summary ---'))
            self.stdout.write(self.style.SUCCESS(f'Successfully migrated {flask_users_migrated} users.'))
            self.stdout.write(self.style.WARNING(f'Skipped {flask_users_skipped} users.'))

        except sqlite3.Error as e:
            self.stderr.write(self.style.ERROR(f'SQLite error: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
        finally:
            if conn:
                conn.close()
