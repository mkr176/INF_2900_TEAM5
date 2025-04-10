# -*- coding: utf-8 -*-
"""
Unit tests for backend scripts like seeds.py.
Focuses on testing script logic in isolation using mocks.
"""
import json
import os
# --- MODIFIED IMPORT ---
from unittest.mock import patch, mock_open, MagicMock, call, ANY # Import 'call' and 'ANY'

from django.test import TestCase
# Import the functions/classes to test
from backend import seeds
from backend.models import UserProfile, Book # Needed for mock spec
from django.contrib.auth import get_user_model

User = get_user_model()

# --- Tests for load_books_from_json ---

class TestLoadBooksFromJson(TestCase):

    @patch('backend.seeds.open', new_callable=mock_open, read_data='[{"title": "Book 1", "isbn": "123"}, {"title": "Book 2", "isbn": "456"}]')
    @patch('backend.seeds.json.load')
    @patch('backend.seeds.os.path.join') # Mock path join to control file path check
    def test_successful_load(self, mock_join, mock_json_load, mock_file_open):
        """Test load_books_from_json successfully reads and parses JSON."""
        # Define the expected path
        expected_path = '/fake/path/to/books_data.json'
        mock_join.return_value = expected_path
        # Define what json.load should return
        expected_data = [{"title": "Book 1", "isbn": "123"}, {"title": "Book 2", "isbn": "456"}]
        mock_json_load.return_value = expected_data

        result = seeds.load_books_from_json()

        # Assertions
        mock_join.assert_called_once() # Check path join was called
        mock_file_open.assert_called_once_with(expected_path, 'r', encoding='utf-8') # Check open called correctly
        mock_json_load.assert_called_once() # Check json.load was called
        self.assertEqual(result, expected_data)

    @patch('backend.seeds.open', side_effect=FileNotFoundError("File not found"))
    @patch('backend.seeds.print') # Mock print to check error message
    @patch('backend.seeds.os.path.join')
    def test_file_not_found(self, mock_join, mock_print, mock_file_open):
        """Test load_books_from_json handles FileNotFoundError."""
        expected_path = '/fake/path/to/books_data.json'
        mock_join.return_value = expected_path

        result = seeds.load_books_from_json()

        # Assertions
        mock_join.assert_called_once()
        mock_file_open.assert_called_once_with(expected_path, 'r', encoding='utf-8')
        self.assertEqual(result, []) # Should return empty list
        mock_print.assert_any_call(f"Error: {expected_path} not found. Please ensure the file exists.") # Check error print

    @patch('backend.seeds.open', new_callable=mock_open, read_data='invalid json')
    @patch('backend.seeds.json.load', side_effect=json.JSONDecodeError("Decode error", "doc", 0))
    @patch('backend.seeds.print')
    @patch('backend.seeds.os.path.join')
    def test_json_decode_error(self, mock_join, mock_print, mock_json_load, mock_file_open):
        """Test load_books_from_json handles JSONDecodeError."""
        expected_path = '/fake/path/to/books_data.json'
        mock_join.return_value = expected_path

        result = seeds.load_books_from_json()

        # Assertions
        mock_join.assert_called_once()
        mock_file_open.assert_called_once_with(expected_path, 'r', encoding='utf-8')
        mock_json_load.assert_called_once()
        self.assertEqual(result, []) # Should return empty list
        # Check that the print message contains the expected error details
        mock_print.assert_any_call(f"Error: Could not decode JSON from {expected_path}. Check format. Details: Decode error: line 1 column 1 (char 0)")

    @patch('backend.seeds.open', side_effect=Exception("Some other error"))
    @patch('backend.seeds.print')
    @patch('backend.seeds.os.path.join')
    def test_other_exception(self, mock_join, mock_print, mock_file_open):
        """Test load_books_from_json handles generic exceptions during file processing."""
        expected_path = '/fake/path/to/books_data.json'
        mock_join.return_value = expected_path

        result = seeds.load_books_from_json()

        # Assertions
        mock_join.assert_called_once()
        mock_file_open.assert_called_once_with(expected_path, 'r', encoding='utf-8')
        self.assertEqual(result, []) # Should return empty list
        mock_print.assert_any_call("An unexpected error occurred loading books: Some other error")


# --- Tests for seed_database ---

# Patch the dependencies for the entire class
@patch('backend.seeds.load_books_from_json')
@patch('backend.seeds.User.objects')
@patch('backend.seeds.UserProfile.objects')
@patch('backend.seeds.Book.objects')
@patch('backend.seeds.print') # Mock print to suppress output during tests unless needed
class TestSeedDatabase(TestCase):

    def test_seed_users_and_profiles(self, mock_print, MockBookObjects, MockUserProfileObjects, MockUserObjects, mock_load_books):
        """Test that users and profiles are created/updated correctly."""
        # Mock load_books to return empty list for this test
        mock_load_books.return_value = []

        # Mock the return values for update_or_create
        # Need to mock the user instance returned to have set_password and save methods
        mock_admin_user = MagicMock(spec=User)
        mock_reg_user = MagicMock(spec=User)
        mock_lib_user = MagicMock(spec=User)

        # Configure update_or_create to return the mock user and a boolean (created)
        MockUserObjects.update_or_create.side_effect = [
            (mock_admin_user, True),  # Admin created
            (mock_reg_user, False), # Regular updated
            (mock_lib_user, True),  # Librarian created
        ]
        MockUserProfileObjects.update_or_create.side_effect = [
            (MagicMock(spec=UserProfile), True), # Admin profile created
            (MagicMock(spec=UserProfile), True), # Regular profile created (even if user updated)
            (MagicMock(spec=UserProfile), True), # Librarian profile created
        ]

        # Call the function
        seeds.seed_database()

        # Assertions for User creation/update
        self.assertEqual(MockUserObjects.update_or_create.call_count, 3)
        MockUserObjects.update_or_create.assert_has_calls([
            call(username='AdminUser', defaults={'username': 'AdminUser', 'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User'}),
            call(username='RegularUser', defaults={'username': 'RegularUser', 'email': 'user@example.com', 'first_name': 'Regular', 'last_name': 'User'}),
            call(username='LibrarianUser', defaults={'username': 'LibrarianUser', 'email': 'librarian@example.com', 'first_name': 'Librarian', 'last_name': 'User'}),
        ], any_order=False) # Order matters here based on the loop in seeds.py

        # Assertions for set_password and save
        self.assertEqual(mock_admin_user.set_password.call_count, 1)
        mock_admin_user.set_password.assert_called_with('admin123')
        self.assertEqual(mock_admin_user.save.call_count, 1)

        self.assertEqual(mock_reg_user.set_password.call_count, 1)
        mock_reg_user.set_password.assert_called_with('user123')
        self.assertEqual(mock_reg_user.save.call_count, 1)

        self.assertEqual(mock_lib_user.set_password.call_count, 1)
        mock_lib_user.set_password.assert_called_with('librarian123')
        self.assertEqual(mock_lib_user.save.call_count, 1)

        # Assertions for UserProfile creation/update
        self.assertEqual(MockUserProfileObjects.update_or_create.call_count, 3)
        MockUserProfileObjects.update_or_create.assert_has_calls([
            call(user=mock_admin_user, defaults={'type': 'AD', 'age': 30}),
            call(user=mock_reg_user, defaults={'type': 'US', 'age': 25}),
            call(user=mock_lib_user, defaults={'type': 'LB', 'age': 35}),
        ], any_order=False)

        # Assert Book seeding was skipped
        MockBookObjects.update_or_create.assert_not_called()


    def test_seed_books_successful(self, mock_print, MockBookObjects, MockUserProfileObjects, MockUserObjects, mock_load_books):
        """Test successful book seeding when users and book data exist."""
        # Mock user creation (only need AdminUser for added_by)
        mock_admin_user = MagicMock(spec=User, username='AdminUser')
        MockUserObjects.update_or_create.side_effect = [
            (mock_admin_user, True), (MagicMock(spec=User), True), (MagicMock(spec=User), True) # Simulate all 3 users
        ]
        # Mock profile creation
        MockUserProfileObjects.update_or_create.return_value = (MagicMock(spec=UserProfile), True)

        # Mock load_books to return sample data
        sample_book_data = [
            {"title": "Book One", "author": "Auth One", "isbn": "978111", "category": "SF", "language": "Eng", "condition": "GD", "publisher": "Pub1", "publication_year": 2020},
            {"title": "Book Two", "author": "Auth Two", "isbn": "978222", "category": "FAN", "language": "Fre", "condition": "NW", "publisher": "Pub2", "publication_year": 2021},
        ]
        mock_load_books.return_value = sample_book_data

        # Mock Book update_or_create
        MockBookObjects.update_or_create.return_value = (MagicMock(spec=Book), True)

        # Call the function
        seeds.seed_database()

        # Assertions
        mock_load_books.assert_called_once()
        self.assertEqual(MockBookObjects.update_or_create.call_count, 2)

        # Check calls to Book.objects.update_or_create with correct defaults and added_by
        expected_defaults_book1 = {
            "title": "Book One", "author": "Auth One", "category": "SF", "language": "Eng",
            "condition": "GD", "available": True, "storage_location": None, "publisher": "Pub1",
            "publication_year": 2020, "copy_number": 1, "added_by": mock_admin_user,
            "borrower": None, "borrow_date": None, "due_date": None, "image": 'images/library_seal.jpg'
        }
        expected_defaults_book2 = {
            "title": "Book Two", "author": "Auth Two", "category": "FAN", "language": "Fre",
            "condition": "NW", "available": True, "storage_location": None, "publisher": "Pub2",
            "publication_year": 2021, "copy_number": 1, "added_by": mock_admin_user,
            "borrower": None, "borrow_date": None, "due_date": None, "image": 'images/library_seal.jpg'
        }

        MockBookObjects.update_or_create.assert_has_calls([
            call(isbn="978111", defaults=expected_defaults_book1),
            call(isbn="978222", defaults=expected_defaults_book2),
        ], any_order=False) # Order matters based on loop


    def test_seed_books_no_admin_user(self, mock_print, MockBookObjects, MockUserProfileObjects, MockUserObjects, mock_load_books):
        """Test book seeding sets added_by=None if AdminUser is not found (or created)."""
        # Mock user creation - DO NOT return an 'AdminUser'
        MockUserObjects.update_or_create.side_effect = [
             (MagicMock(spec=User, username='RegularUser'), True), # Simulate only non-admin users
             (MagicMock(spec=User, username='LibrarianUser'), True),
             # Add a third mock if the loop expects 3 users, ensure none is 'AdminUser'
             (MagicMock(spec=User, username='AnotherUser'), True),
        ]
        MockUserProfileObjects.update_or_create.return_value = (MagicMock(spec=UserProfile), True)

        # Mock load_books
        sample_book_data = [{"title": "Book One", "isbn": "978111", "category": "SF", "language": "Eng", "condition": "GD"}]
        mock_load_books.return_value = sample_book_data

        # Mock Book update_or_create
        MockBookObjects.update_or_create.return_value = (MagicMock(spec=Book), True)

        # Call the function
        seeds.seed_database()

        # Assertions
        mock_load_books.assert_called_once()
        self.assertEqual(MockBookObjects.update_or_create.call_count, 1)

        # Check that added_by is None in the defaults
        call_args, call_kwargs = MockBookObjects.update_or_create.call_args
        self.assertEqual(call_kwargs['isbn'], "978111")
        self.assertIsNone(call_kwargs['defaults']['added_by']) # Key assertion
        # Check print warning message
        mock_print.assert_any_call("Warning: AdminUser not found. 'added_by' for books will be set to None.")


    def test_seed_books_no_book_data(self, mock_print, MockBookObjects, MockUserProfileObjects, MockUserObjects, mock_load_books):
        """Test book seeding is skipped if load_books_from_json returns empty."""
        # Mock user/profile creation (doesn't matter which users for this test)
        MockUserObjects.update_or_create.return_value = (MagicMock(spec=User), True)
        MockUserProfileObjects.update_or_create.return_value = (MagicMock(spec=UserProfile), True)

        # Mock load_books to return empty list
        mock_load_books.return_value = []

        # Call the function
        seeds.seed_database()

        # Assertions
        mock_load_books.assert_called_once()
        # Book seeding loop should not run
        MockBookObjects.update_or_create.assert_not_called()
        # Check print message
        mock_print.assert_any_call("No book data loaded or found. Skipping book seeding.")


    def test_seed_books_skips_missing_isbn(self, mock_print, MockBookObjects, MockUserProfileObjects, MockUserObjects, mock_load_books):
        """Test book seeding skips entries with missing ISBN."""
        # Mock user/profile creation
        mock_admin_user = MagicMock(spec=User, username='AdminUser')
        MockUserObjects.update_or_create.side_effect = [(mock_admin_user, True)] * 3 # Assume admin exists
        MockUserProfileObjects.update_or_create.return_value = (MagicMock(spec=UserProfile), True)

        # Mock load_books with one missing ISBN
        sample_book_data = [
            {"title": "Book One", "author": "Auth One", "isbn": "978111", "category": "SF"},
            {"title": "Book Two - No ISBN", "author": "Auth Two", "category": "FAN"}, # Missing ISBN
            {"title": "Book Three", "author": "Auth Three", "isbn": "978333", "category": "HIS"},
        ]
        mock_load_books.return_value = sample_book_data

        # Mock Book update_or_create
        MockBookObjects.update_or_create.return_value = (MagicMock(spec=Book), True)

        # Call the function
        seeds.seed_database()

        # Assertions
        mock_load_books.assert_called_once()
        # Should only be called for books with ISBN
        self.assertEqual(MockBookObjects.update_or_create.call_count, 2)
        MockBookObjects.update_or_create.assert_has_calls([
            call(isbn="978111", defaults=ANY), # ANY used for brevity, checked in other tests
            call(isbn="978333", defaults=ANY),
        ], any_order=False)
        # Check print message for skipped book
        mock_print.assert_any_call("Skipping book due to missing ISBN: Book Two - No ISBN")