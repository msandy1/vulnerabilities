from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # Remove first_name, last_name if 'name' is meant to be the full name
    # Or, keep them and make 'name' an additional field if it serves a different purpose
    first_name = None  # Example: removing default first_name
    last_name = None   # Example: removing default last_name

    name = models.CharField(max_length=255, blank=True, help_text="User's full name.")
    registered_on = models.DateTimeField(default=timezone.now, help_text="The date and time this user registered.")
    # is_admin from Flask model maps to is_staff or is_superuser in Django.
    # AbstractUser already has is_staff and is_superuser.
    # username, email, password, is_active, date_joined are also part of AbstractUser.

    def __str__(self):
        return self.username
