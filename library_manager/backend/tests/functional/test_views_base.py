# -*- coding: utf-8 -*-
"""
Base test case for library API endpoints.
Contains common setup data and helper methods used across different test files.
"""
from datetime import date, timedelta

from django.urls import reverse
from django.contrib.auth import get_user_model, SESSION_KEY
from rest_framework.test import APITestCase

from backend.models import Book, UserProfile
from backend.views import MAX_BORROW_LIMIT # Import borrow limit

# Get the User model
User = get_user_model()

# Define constants for user types (matching models.py)
ADMIN_TYPE = 'AD'
LIBRARIAN_TYPE = 'LB'
USER_TYPE = 'US'

# Define constants for book details
TEST_BOOK_ISBN = '978-3-16-148410-0'
TEST_BOOK_ISBN_2 = '978-1-23-456789-7'
TEST_BOOK_ISBN_3 = '978-0-00-000000-3' # For borrowed book
TEST_BOOK_ISBN_4 = '978-1-11-111111-1' # For creation tests
TEST_BOOK_ISBN_5 = '978-2-22-222222-2' # For filtering/searching

class LibraryAPITestCaseBase(APITestCase):
    """
    Base test case providing common setup for library API tests.
    Inherit from this class in specific test files (e.g., test_auth_views.py).
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        This runs once per class inheriting from this base.
        """
        # --- Create Users ---
        # Admin User
        cls.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@example.com',
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.create(user=cls.admin_user, type=ADMIN_TYPE, age=35)

        # Librarian User
        cls.librarian_user = User.objects.create_user(
            username='testlibrarian',
            email='librarian@example.com',
            password='password123',
            first_name='Librarian',
            last_name='User'
        )
        UserProfile.objects.create(user=cls.librarian_user, type=LIBRARIAN_TYPE, age=40)

        # Regular User 1
        cls.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@example.com',
            password='password123',
            first_name='Regular',
            last_name='UserOne'
        )
        UserProfile.objects.create(user=cls.user1, type=USER_TYPE, age=25)

        # Regular User 2
        cls.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@example.com',
            password='password123',
            first_name='Regular',
            last_name='UserTwo'
        )
        UserProfile.objects.create(user=cls.user2, type=USER_TYPE, age=30)

        # --- Create Books ---
        cls.book1 = Book.objects.create(
            title='The Test Book',
            author='Author One',
            isbn=TEST_BOOK_ISBN,
            category='SF', # Science Fiction
            language='English',
            added_by=cls.librarian_user,
            condition='GD', # Good
            available=True,
            publication_year=2020
        )

        cls.book2 = Book.objects.create(
            title='Another Test Title',
            author='Author Two',
            isbn=TEST_BOOK_ISBN_2,
            category='HIS', # History
            language='Spanish',
            added_by=cls.admin_user,
            condition='NW', # New
            available=True,
            publication_year=2021
        )

        # Book initially borrowed by user1 for testing return/borrowed list logic
        cls.borrowed_book = Book.objects.create(
            title="Already Borrowed",
            author="Author Three",
            isbn=TEST_BOOK_ISBN_3,
            category="FAN", # Fantasy
            language="English",
            added_by=cls.librarian_user,
            condition='FR', # Fair
            available=False, # Not available
            borrower=cls.user1, # Borrowed by user1
            borrow_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9) # Due in 9 days
        )

        # Book for filtering/searching tests
        cls.book_for_filter = Book.objects.create(
            title='Crime and Mystery',
            author='Author One', # Same author as book1
            isbn=TEST_BOOK_ISBN_5,
            category='CR', # Crime
            language='English',
            added_by=cls.librarian_user,
            condition='GD', # Good
            available=True,
            publication_year=2022
        )


        # --- Define URLs (using reverse for maintainability) ---
        # Auth
        cls.register_url = reverse('backend:register')
        cls.login_url = reverse('backend:login')
        cls.logout_url = reverse('backend:logout')
        # User Management
        cls.user_list_url = reverse('backend:user-list')
        cls.current_user_url = reverse('backend:current-user')
        cls.current_user_update_url = reverse('backend:current-user-update')
        # Detail URLs need an ID, generated within tests using reverse
        cls.user_detail_url = lambda user_id: reverse('backend:user-detail', kwargs={'id': user_id})
        # Book Management
        cls.book_list_create_url = reverse('backend:book-list-create')
        cls.borrowed_books_list_url = reverse('backend:borrowed-books-list')
        # Detail/Action URLs need an ID, generated within tests using reverse
        cls.book_detail_url = lambda book_id: reverse('backend:book-detail', kwargs={'id': book_id})
        cls.book_borrow_url = lambda book_id: reverse('backend:book-borrow', kwargs={'book_id': book_id})
        cls.book_return_url = lambda book_id: reverse('backend:book-return', kwargs={'book_id': book_id})
        # Security
        cls.csrf_token_url = reverse('backend:csrf-token')

    def setUp(self):
        """
        Set up run before every test method.
        Use this for things that might change during a test, like client authentication.
        """
        # Ensure client is logged out before each test by default
        self.client.logout()

    # --- Helper Methods ---
    def _login_user(self, user_type='user1'): # Default to user1 for simplicity
        """Logs in a user based on type ('admin', 'librarian', 'user1', 'user2')."""
        if user_type == 'admin':
            user = self.admin_user
        elif user_type == 'librarian':
            user = self.librarian_user
        elif user_type == 'user1':
            user = self.user1
        elif user_type == 'user2':
            user = self.user2
        else: # Fallback or raise error if needed
             user = self.user1

        # Use force_login for simplicity in tests, bypassing the login view
        self.client.force_login(user)
        # Alternatively, use the login view:
        # login_data = {'username': user.username, 'password': 'password123'}
        # response = self.client.post(self.login_url, login_data)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        return user