from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User # Assuming your custom user model is named User

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    # Add 'name' and 'registered_on' to the list display
    # Ensure 'email' is present as first_name/last_name are removed.
    list_display = ('username', 'email', 'name', 'registered_on', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    # Add 'name' to search fields. 'email' is usually already in BaseUserAdmin.search_fields.
    search_fields = BaseUserAdmin.search_fields + ('name',)
    # Add 'registered_on' to list filters.
    list_filter = BaseUserAdmin.list_filter + ('registered_on',)

    # Customize the add/change user forms
    # Our custom User model removed first_name, last_name and added 'name'.
    # 'date_joined' is available from AbstractUser, 'registered_on' is our custom field.
    # 'registered_on' should be readonly as it's set on creation (default=timezone.now).
    # 'date_joined' is also auto-set.

    # Modifying fieldsets from BaseUserAdmin:
    # Original BaseUserAdmin.fieldsets:
    # (None, {'fields': ('username', 'password')}),
    # ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
    # ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    # ('Important dates', {'fields': ('last_login', 'date_joined')})

    # We need to replace 'first_name', 'last_name' with 'name'
    # and add 'registered_on' to 'Important dates'.

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'email')}), # Replaced first_name, last_name with name
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'registered_on')}), # Added registered_on
    )

    # Make 'registered_on' and 'date_joined' read-only in the admin form.
    # BaseUserAdmin.readonly_fields usually already includes 'last_login' and 'date_joined' by default
    # when adding a user, but explicitly adding 'date_joined' here ensures it's readonly on change forms too.
    # For 'registered_on', it needs to be added.
    readonly_fields = ('last_login', 'date_joined', 'registered_on')


# Register the new User admin, unregistering the default if User is swapped
# admin.site.unregister(User) # This might be needed if User was previously registered by Django's default
admin.site.register(User, UserAdmin)

# To ensure any other models from django.contrib.auth that might have been registered
# with the default User are handled correctly if they were, this is generally not needed
# unless complex swapping scenarios. For a simple AUTH_USER_MODEL swap, Django handles it.
# from django.contrib.auth.models import Group
# if admin.site.is_registered(Group):
#     admin.site.unregister(Group)
# admin.site.register(Group) # Re-register Group if needed, usually not.
