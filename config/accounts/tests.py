from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserAPITests(APITestCase):
    def setUp(self):
        self.register_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
            "name": "Test User Name"
        }
        self.login_data = {
            "username": "testuser",
            "password": "StrongPassword123"
        }
        # Create an admin user for admin site tests
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword"
        )
        # Create a regular user that can be used for general authentication tests not starting with registration
        # For example, if we want to test login without registering in the same test method.
        # However, most tests here perform registration first.

    def test_user_registration_success(self):
        """Test user registration success."""
        url = reverse("user_register") # Name from accounts.urls
        response = self.client.post(url, self.register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        # Count is 2 because admin_user + new testuser
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username="testuser").email, "testuser@example.com")
        self.assertTrue(User.objects.get(username="testuser").name == "Test User Name")

    def test_user_registration_password_mismatch(self):
        """Test registration password mismatch."""
        data = self.register_data.copy()
        data["password2"] = "WrongPassword"
        url = reverse("user_register")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("password", response.data)

    def test_user_registration_existing_username(self):
        """Test registration with existing username."""
        self.client.post(reverse("user_register"), self.register_data, format="json") # First registration
        # Attempt to register the same user again
        response = self.client.post(reverse("user_register"), self.register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("username", response.data)

    def test_user_login_success_and_token_generation(self):
        """Test user login success and token generation."""
        self.client.post(reverse("user_register"), self.register_data, format="json") # Register user first
        url = reverse("token_obtain_pair") # Name from simplejwt urls or accounts.urls
        response = self.client.post(url, self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        self.client.post(reverse("user_register"), self.register_data, format="json")
        invalid_data = {"username": "testuser", "password": "WrongPassword"}
        url = reverse("token_obtain_pair")
        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_get_user_detail_authenticated(self):
        """Test get user detail when authenticated."""
        self.client.post(reverse("user_register"), self.register_data, format="json")
        login_response = self.client.post(reverse("token_obtain_pair"), self.login_data, format="json")
        access_token = login_response.data["access"]
        url = reverse("user_detail") # Name from accounts.urls
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["username"], self.register_data["username"])
        self.assertEqual(response.data["email"], self.register_data["email"])
        self.assertEqual(response.data["name"], self.register_data["name"])

    def test_get_user_detail_unauthenticated(self):
        """Test get user detail when unauthenticated."""
        url = reverse("user_detail")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_admin_site_accessible_by_admin(self):
        """Test admin site is accessible by admin user."""
        # Login the admin user
        self.client.force_login(self.admin_user)
        # Try to access the main admin page
        admin_index_url = reverse("admin:index")
        response = self.client.get(admin_index_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Removed response.data

    def test_user_logout(self):
        """Test user logout and token blacklisting."""
        # Register and login user
        self.client.post(reverse("user_register"), self.register_data, format="json")
        login_url = reverse("token_obtain_pair")
        login_response = self.client.post(login_url, self.login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK, login_response.data)
        refresh_token = login_response.data["refresh"]
        access_token = login_response.data["access"]

        # Verify token is active by accessing a protected route
        user_detail_url = reverse("user_detail")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Logout user
        logout_url = reverse("user_logout") # Name from accounts.urls
        response = self.client.post(logout_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Verify refresh token is blacklisted (cannot be used to get a new access token)
        refresh_url = reverse("token_refresh") # Name from simplejwt urls or accounts.urls
        response = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)
        if response.data: # Check if response.data is not None
             self.assertIn("token_not_valid", response.data.get("code", ""))
