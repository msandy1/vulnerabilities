from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView # TokenRefreshView is not directly used here but in urls
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserDetailSerializer

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all() # Not strictly necessary for CreateAPIView but good practice
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

class UserLoginView(TokenObtainPairView):
    # Uses SimpleJWT's default serializer TokenObtainPairSerializer
    # and default TokenObtainPairView behavior
    permission_classes = [permissions.AllowAny]

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can logout

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle specific exceptions like TokenError from simplejwt if needed for more detailed errors
            return Response({"error": "Logout failed. Invalid token or server error.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    # queryset = User.objects.all() # Not needed if get_object is overridden
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can see/update their details

    def get_object(self):
        # Returns the currently authenticated user
        # No need to lookup by pk from URL if we always want the request.user
        return self.request.user

    # Ensure that users cannot make themselves staff or superuser via this endpoint
    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True # Allow partial updates (PATCH)
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Prevent users from escalating privileges
        # Ensure 'is_staff' and 'is_superuser' are not in request.data for non-superusers
        user_is_trying_to_elevate_privileges = any(field in request.data for field in ['is_staff', 'is_superuser'])

        if user_is_trying_to_elevate_privileges and not request.user.is_superuser:
            # Create a mutable copy of request.data
            data_copy = request.data.copy()
            # Remove potentially malicious fields
            data_copy.pop('is_staff', None)
            data_copy.pop('is_superuser', None)
            # Replace request.data with the sanitized version for the super().update call
            # This is a bit of a hack. A cleaner way might be to use a different serializer for updates
            # or to handle this logic within the serializer's validate method.
            # However, for a view-level check, this can work.
            # Be cautious with modifying request.data directly if it's an immutable QueryDict.
            # request._data = data_copy # This is modifying a protected member, not ideal
            # Instead, pass the modified data to the serializer if possible,
            # or perform validation and raise error if forbidden fields are present.

            # For now, let's just forbid the update if these fields are present for non-superusers
            if 'is_staff' in request.data and request.data['is_staff'] != self.request.user.is_staff:
                 return Response({"error": "You do not have permission to change staff status."}, status=status.HTTP_403_FORBIDDEN)
            if 'is_superuser' in request.data and request.data['is_superuser'] != self.request.user.is_superuser:
                 return Response({"error": "You do not have permission to change superuser status."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)


from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"
    # Add permission_classes if these pages require authentication
    # permission_classes = [permissions.AllowAny] # Or IsAuthenticated

class SiteLoginView(TemplateView):
    template_name = "login.html"
    # permission_classes = [permissions.AllowAny]

class SiteRegistrationView(TemplateView):
    template_name = "registration.html"
    # permission_classes = [permissions.AllowAny]

class SiteAccountView(TemplateView):
    template_name = "account.html"
    # permission_classes = [permissions.IsAuthenticated] # Likely requires login
