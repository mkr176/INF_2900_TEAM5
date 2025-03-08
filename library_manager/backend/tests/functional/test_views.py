from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.auth.models import User


class MyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("index")
        # Create a user for login tests
        self.test_user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_index_view(self):
        """Test that the index view returns a 200 status code and uses the correct template."""
        # Request the root URL.  This will be caught by the catch-all route.
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "startpage.html")

    def test_server_running(self):
        """Test that the server is running and returns a 200 status code for the index view."""
        response = self.client.get(self.index_url)  # use the index_url
        self.assertEqual(response.status_code, 200)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("signup")

    def test_user_registration_successful(self):
        """Test successful user registration."""
        response = self.client.post(
            self.register_url,
            json.dumps({"username": "newuser", "password": "password123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "User registered successfully"})
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_registration_username_exists(self):
        """Test registration with an existing username."""
        User.objects.create_user(username="existinguser", password="password123")
        response = self.client.post(
            self.register_url,
            json.dumps({"username": "existinguser", "password": "anotherpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Username already exists"})

    def test_user_registration_invalid_json(self):
        """Test registration with invalid JSON data."""
        response = self.client.post(
            self.register_url, "invalid json data", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON"})


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            username="testloginuser", password="testpassword"
        )

    def test_user_login_successful(self):
        """Test successful user login."""
        response = self.client.post(
            self.login_url,
            json.dumps({"username": "testloginuser", "password": "testpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Login successful"})
        self.assertTrue(
            self.client.login(username="testloginuser", password="testpassword")
        )

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            self.login_url,
            json.dumps({"username": "testloginuser", "password": "wrongpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Invalid credentials"})
        self.assertFalse(
            self.client.login(username="testloginuser", password="wrongpassword")
        )

    def test_user_login_missing_fields(self):
        """Test login with missing username or password."""
        response = self.client.post(
            self.login_url,
            json.dumps({"username": "testloginuser"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"error": "Username and password are required"}
        )

    def test_user_login_invalid_json(self):
        """Test login with invalid JSON data."""
        response = self.client.post(
            self.login_url, "invalid json data", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON"})


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(
            username="testlogoutuser", password="testpassword"
        )
        self.client.login(
            username="testlogoutuser", password="testpassword"
        )  # Login user before logout test

    def test_user_logout_successful(self):
        """Test successful user logout."""
        self.assertTrue(
            self.client.login(username="testlogoutuser", password="testpassword")
        )  # Check user is logged in before logout
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Logout successful"})
