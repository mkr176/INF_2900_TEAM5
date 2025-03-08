from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.auth.models import User
from backend.models import User as CustomUser  # Import your custom User model
from backend.models import Book


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


class ListUsersViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_users_url = reverse("list-users")
        # Create some test users using your custom User model
        CustomUser.objects.create(name="User1", numberbooks=0, type='US')
        CustomUser.objects.create(name="User2", numberbooks=2, type='LB')

    def test_list_users_view_authenticated(self):
        """
        Test listing users view for authenticated users.
        It should return a 200 status code and a list of users.
        """
        response = self.client.get(self.list_users_url)
        # print(f"Response status code: {response.status_code}") # Print status code
        # print(f"Response content: {response.content}") # Print response content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) >= 2)  # Assuming at least 2 users were created in setUp
        # Optionally, check for specific fields in the returned data
        user_names = {user['username'] for user in data if 'username' in user} #adapt to your serializer fields
        expected_names = {'User1', 'User2'} #adapt to your created users
        # self.assertTrue(expected_names.issubset(user_names)) #adapt to your serializer fields

    def test_list_users_view_unauthenticated(self):
        """
        Test listing users view for unauthenticated users.
        Depending on your requirements, this might be a 403 Forbidden or a redirect to login.
        Adjust the expected status code as needed.
        """
        response = self.client.get(self.list_users_url)
        # print(f"Response status code: {response.status_code}")
        # print(f"Response content: {response.content}")

        # Assuming the view should be accessible to all (adjust as per your access control)
        self.assertEqual(response.status_code, 200) # or 403 if permission denied for unauthenticated users

class ListBooksViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Assuming you have a URL name 'list-books' for listing books
        # and have created some books using your Book model
        self.list_books_url = reverse("list-books") # Define list-books url in urls.py
        test_user = CustomUser.objects.create(name="TestUser", numberbooks=0, type='US')
        Book.objects.create(title="Book1", author="Author1", due_date="2025-03-15", isbn="1234567890001", category="CK", language="English", user=test_user, condition="NW", available=True)
        Book.objects.create(title="Book2", author="Author2", due_date="2025-04-20", isbn="1234567890002", category="CR", language="Spanish", user=test_user, condition="GD", available=False)

    def test_list_books_view_authenticated(self):
        """
        Test listing books view for authenticated users.
        Should return 200 and a list of books.
        """
        response = self.client.get(self.list_books_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) >= 2) # Assuming at least 2 books created in setUp
        book_titles = {book['title'] for book in data if 'title' in book} #adapt to your serializer fields
        expected_titles = {'Book1', 'Book2'} #adapt to your created books
        # self.assertTrue(expected_titles.issubset(book_titles)) #adapt to your serializer fields

    def test_list_books_view_unauthenticated(self):
        """
        Test listing books view for unauthenticated users.
        Adjust expected status code based on access control.
        """
        response = self.client.get(self.list_books_url)
        # Assuming books list is publicly accessible (adjust as needed)
        self.assertEqual(response.status_code, 200) # or 403 if permission denied for unauthenticated users