from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'), # For obtaining token
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # For refreshing token
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/', UserDetailView.as_view(), name='user_detail'), # To get/update current user's details
]
