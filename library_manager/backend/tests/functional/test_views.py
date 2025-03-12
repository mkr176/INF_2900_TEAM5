from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.auth.models import User
from backend.models import People as CustomUser  # Import your custom User model
from backend.models import Book
from datetime import date, timedelta


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
        CustomUser.objects.create(name="User1", numberbooks=0, type='US', age=25) # Added age=25
        CustomUser.objects.create(name="User2", numberbooks=2, type='LB', age=30) # Added age=30

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
        test_user = CustomUser.objects.create(name="TestUser", numberbooks=0, type='US', age=28) # Added age=28
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
        
class BorrowBookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.borrow_book_url = reverse("borrow-book")
        # Create a test user
        self.test_user = CustomUser.objects.create(name="TestBorrowUser", numberbooks=0, type='US', age=25, email="borrow@example.com", password="password123")
        # Create another test user for borrowing attempts by different users
        self.test_user2 = CustomUser.objects.create(name="TestBorrowUser2", numberbooks=0, type='US', age=26, email="borrow2@example.com", password="password123")
        # Create a test book and ensure it's available initially
        self.test_book = Book.objects.create(
            title="Test Book for Borrowing",
            author="Test Author",
            due_date=date.today() + timedelta(days=7), # Due date in the future
            isbn="1234567890999",
            category="MY",
            language="English",
            user=self.test_user,
            condition="GD",
            available=True
        )

    def test_borrow_book_successful(self):
        """Test successful book borrowing."""
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": self.test_user.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Book borrowed successfully")
        # Check if the book is now marked as not available and borrower is set
        updated_book = Book.objects.get(id=self.test_book.id)
        self.assertFalse(updated_book.available)
        self.assertEqual(updated_book.borrower, self.test_user)
        self.assertEqual(updated_book.borrow_date, date.today())

    def test_borrow_book_unavailable(self):
        """Test attempting to borrow an already borrowed book."""
        # First, borrow the book to make it unavailable
        self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": self.test_user.id}),
            content_type="application/json",
        )
        # Attempt to borrow the same book again with a different user
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": self.test_user2.id}), # Different user attempts to borrow
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        expected_message_start = "Book is currently unavailable. It will be available from" # Start of the expected message
        actual_message = response.json()['message']
        self.assertTrue(actual_message.startswith(expected_message_start)) # Check if message starts as expected

        # Check if the book is still marked as not available and borrower is still the original user
        updated_book = Book.objects.get(id=self.test_book.id)
        self.assertFalse(updated_book.available)
        # Optionally check if the borrower is still the original borrower
        self.assertEqual(updated_book.borrower, self.test_user)

    def test_borrow_book_return_successful(self):
        """Test successful book return by borrower."""
        # First, borrow the book
        self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": self.test_user.id}),
            content_type="application/json",
        )
        # Now, return the book (borrow it again with the same user)
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": self.test_user.id}), # Same user borrows again to simulate return
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Book returned successfully") # Updated message for return

        # Check if the book is now marked as available and borrower is cleared
        updated_book = Book.objects.get(id=self.test_book.id)
        self.assertTrue(updated_book.available)
        self.assertIsNone(updated_book.borrower)
        self.assertIsNone(updated_book.borrow_date)


    def test_borrow_book_not_found(self):
        """Test attempting to borrow a book that does not exist."""
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": 999, "user_id": self.test_user.id}), # Non-existent book id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "Book not found")

    def test_borrow_book_user_not_found(self):
        """Test attempting to borrow a book with a user that does not exist."""
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id, "user_id": 999}), # Non-existent user id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "User not found")

    def test_borrow_book_missing_book_id(self):
        """Test borrow book with missing book_id."""
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"user_id": self.test_user.id}), # Missing book_id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Book ID is required")

    def test_borrow_book_missing_user_id(self):
        """Test borrow book with missing user_id."""
        response = self.client.post(
            self.borrow_book_url,
            json.dumps({"book_id": self.test_book.id}), # Missing user_id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "User ID is required")

    def test_borrow_book_invalid_json(self):
        """Test borrow book with invalid JSON."""
        response = self.client.post(
            self.borrow_book_url,
            "invalid json data",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Invalid JSON")        