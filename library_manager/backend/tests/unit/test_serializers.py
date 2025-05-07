# -*- coding: utf-8 -*-
"""
Unit tests for backend serializers.
"""
from datetime import date, timedelta
import copy # Import copy for deepcopy checks if needed later

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError # For model validation
from rest_framework.exceptions import ValidationError as DRFValidationError # For serializer validation
# <<< CHANGED: Import HttpRequest directly >>>
from django.http import HttpRequest
from django.test import RequestFactory
# Keep DRFRequest import if needed elsewhere, but avoid passing it in context
from rest_framework.request import Request as DRFRequest


from backend.serializers import (
    UserProfileSerializer,
    UserSerializer,
    RegisterSerializer,
    BookSerializer,
)
from backend.models import UserProfile, Book
from ..factories import UserFactory, UserProfileFactory, BookFactory

User = get_user_model()

# --- UserProfileSerializer Tests ---

class UserProfileSerializerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(username="profiletestuser")
        cls.profile = UserProfileFactory(user=cls.user, type='LB', age=33)
        # <<< CHANGED: Create a raw HttpRequest for context >>>
        factory = RequestFactory()
        cls.http_request = factory.get('/fake-url/')
        # Assign user if needed by serializer context logic (e.g., permissions)
        cls.http_request.user = cls.user
        # Pass the raw HttpRequest in the context
        cls.serializer = UserProfileSerializer(instance=cls.profile, context={'request': cls.http_request})


    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        # Accessing .data should not cause recursion if context is HttpRequest
        data = self.serializer.data
        expected_keys = {
            "user_id", "username", "type", "age", "avatar", "get_type_display",
            "avatar_url"
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_field_content(self):
        """Verify the content of the serialized fields is correct."""
        data = self.serializer.data
        self.assertEqual(data['user_id'], self.user.id)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['type'], 'LB')
        self.assertEqual(data['get_type_display'], 'Librarian')
        self.assertEqual(data['age'], 33)
        self.assertTrue(data['avatar'].endswith('avatars/default.svg'))
        # Check the generated avatar_url (build_absolute_uri might behave differently with HttpRequest vs DRFRequest)
        # We might need to adjust the assertion if it only returns the path now.
        # Let's assume build_absolute_uri still works or the test focuses on the path.
        self.assertTrue(data['avatar_url'].endswith('/static/images/avatars/default.svg'))


    def test_read_only_fields(self):
        """Verify read-only fields cannot be updated via the serializer."""
        update_data = {
            "username": "newusername", # Read-only derived field
            "user_id": self.user.id + 1, # Read-only derived field
            "get_type_display": "Admin", # Read-only method field
            "avatar_url": "http://example.com/new.jpg", # Read-only method field
            "type": "AD", # Writable field
            "age": 40,    # Writable field
        }
        # <<< CHANGED: Use HttpRequest in context >>>
        factory = RequestFactory()
        http_request = factory.patch('/fake-url/')
        http_request.user = self.user # Assign user if needed
        serializer = UserProfileSerializer(instance=self.profile, data=update_data, partial=True, context={'request': http_request})

        self.assertTrue(serializer.is_valid())
        self.assertNotIn('username', serializer.validated_data)
        self.assertNotIn('user_id', serializer.validated_data)
        self.assertNotIn('get_type_display', serializer.validated_data)
        self.assertNotIn('avatar_url', serializer.validated_data)
        self.assertIn('type', serializer.validated_data)
        self.assertIn('age', serializer.validated_data)

        profile = serializer.save()
        self.assertEqual(profile.user.username, "profiletestuser")
        self.assertEqual(profile.type, "AD")
        self.assertEqual(profile.age, 40)


# --- UserSerializer Tests ---

class UserSerializerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="userserializertest",
            email="user@test.com",
            first_name="Test",
            last_name="User"
        )
        cls.profile = UserProfileFactory(user=cls.user, type='US', age=29)
        # <<< CHANGED: Create a raw HttpRequest for context >>>
        factory = RequestFactory()
        cls.http_request = factory.get('/fake-url/')
        cls.http_request.user = cls.user
        # Pass the raw HttpRequest in the context
        cls.serializer = UserSerializer(instance=cls.user, context={'request': cls.http_request})


    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        data = self.serializer.data
        expected_keys = {
            "id", "username", "email", "first_name", "last_name",
            "profile", "date_joined", "is_staff"
        }
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertNotIn("password", data)

    def test_field_content(self):
        """Verify the content of the serialized fields is correct."""
        data = self.serializer.data
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertIsNotNone(data['date_joined'])
        self.assertFalse(data['is_staff'])

    def test_nested_profile_serialization(self):
        """Verify the nested profile data is serialized correctly."""
        data = self.serializer.data
        self.assertIn('profile', data)
        profile_data = data['profile']
        self.assertIsInstance(profile_data, dict)
        self.assertEqual(profile_data['user_id'], self.user.id)
        self.assertEqual(profile_data['username'], self.user.username)
        self.assertEqual(profile_data['type'], 'US')
        self.assertEqual(profile_data['age'], 29)
        self.assertTrue(profile_data['avatar_url'].endswith('/static/images/avatars/default.svg'))


    def test_update_user(self):
        """Verify the serializer can update user fields (excluding password)."""
        update_data = {
            "first_name": "UpdatedFirst",
            "email": "updated@test.com"
        }
        # Context might not be strictly needed for basic field updates
        serializer = UserSerializer(instance=self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "UpdatedFirst")
        self.assertEqual(updated_user.email, "updated@test.com")
        self.assertEqual(updated_user.username, self.user.username)

    def test_password_is_write_only(self):
        """Verify password field is write-only."""
        update_data = {"password": "newpassword123"}
        serializer = UserSerializer(instance=self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        # Accessing .data should not include 'password'
        self.assertNotIn('password', serializer.data)


# --- RegisterSerializer Tests ---

# RegisterSerializer doesn't use context['request'] directly, so no changes needed here.
class RegisterSerializerTests(TestCase):

    def test_valid_registration(self):
        """Test successful registration with valid data."""
        valid_data = {
            "username": "newreguser",
            "email": "newreg@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
            "first_name": "Reg",
            "last_name": "User",
            "type": "LB",
            "age": 45,
        }
        serializer = RegisterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, valid_data["username"])
        self.assertEqual(user.email, valid_data["email"])
        self.assertTrue(user.check_password(valid_data["password"]))
        self.assertEqual(user.first_name, valid_data["first_name"])
        self.assertEqual(user.last_name, valid_data["last_name"])

        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.type, valid_data["type"])
        self.assertEqual(user.profile.age, valid_data["age"])

    def test_registration_default_profile_type(self):
        """Test registration uses default profile type ('US') if not provided."""
        valid_data = {
            "username": "defaulttypeuser",
            "email": "default@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
        }
        serializer = RegisterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.type, 'US')

    def test_password_mismatch(self):
        """Test registration fails if passwords do not match."""
        invalid_data = {
            "username": "pwmissmatch",
            "email": "pwmiss@example.com",
            "password": "ValidPassword123",
            "password2": "DifferentPassword123",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', cm.exception.detail)
        self.assertIn("didn't match", str(cm.exception.detail['password'][0]).lower())

    def test_duplicate_username(self):
        """Test registration fails with a duplicate username."""
        UserFactory(username="existinguser")
        invalid_data = {
            "username": "existinguser",
            "email": "unique@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('username', cm.exception.detail)
        self.assertIn("already exists", str(cm.exception.detail['username'][0]).lower())

    def test_duplicate_email(self):
        """Test registration fails with a duplicate email."""
        UserFactory(username="uniqueuser", email="existing@example.com")
        invalid_data = {
            "username": "anotheruniqueuser",
            "email": "existing@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('email', cm.exception.detail)
        self.assertIn("already exists", str(cm.exception.detail['email'][0]).lower())

    def test_missing_required_fields(self):
        """Test registration fails if required fields are missing."""
        required_fields = ["username", "email", "password", "password2"]
        for field in required_fields:
            invalid_data = {
                "username": "missingtest",
                "email": "missing@example.com",
                "password": "ValidPassword123",
                "password2": "ValidPassword123",
            }
            del invalid_data[field]
            serializer = RegisterSerializer(data=invalid_data)
            with self.assertRaises(DRFValidationError) as cm:
                serializer.is_valid(raise_exception=True)
            self.assertIn(field, cm.exception.detail, f"Validation error for missing field '{field}' not found.")

    def test_weak_password(self):
        """Test registration fails with a weak password (e.g., too short)."""
        invalid_data = {
            "username": "weakpwuser",
            "email": "weak@example.com",
            "password": "pw",
            "password2": "pw",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', cm.exception.detail)
        self.assertTrue(any("too short" in str(e).lower() or "minimum length" in str(e).lower() for e in cm.exception.detail['password']))

    def test_invalid_profile_type_choice(self):
        """Test registration fails with an invalid choice for profile type."""
        invalid_data = {
            "username": "invalidtypeuser",
            "email": "invalidtype@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
            "type": "XX",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('type', cm.exception.detail)
        self.assertIn("is not a valid choice", str(cm.exception.detail['type'][0]).lower())


# --- BookSerializer Tests ---

class BookSerializerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.adder = UserFactory(username="bookadder")
        # Ensure cls.adder (who acts as request.user) is a Librarian
        # This allows viewing borrower details as per BookSerializer.get_borrower logic
        UserProfileFactory(user=cls.adder, type='LB') 
        cls.borrower = UserFactory(username="bookborrower")
        cls.book_available = BookFactory(
            title="Available Book", isbn="9781111111111", category="SF", condition="GD",
            added_by=cls.adder, available=True, borrower=None, borrow_date=None, due_date=None,
            image='test_cover.jpg'
        )
        cls.book_borrowed = BookFactory(
            title="Borrowed Book", isbn="9782222222222", category="HIS", condition="FR",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9)
        )
        cls.book_overdue = BookFactory(
            title="Overdue Book", isbn="9783333333333", category="FAN", condition="PO",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6)
        )
        cls.book_due_today = BookFactory(
            title="Due Today Book", isbn="9784444444444", category="ROM", condition="NW",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=14),
            due_date=date.today()
        )
        # <<< CHANGED: Create a raw HttpRequest for context >>>
        cls.factory = RequestFactory()
        cls.http_request = cls.factory.get('/fake-url/')
        # Assign user if needed by serializer context logic
        cls.http_request.user = cls.adder # Or any relevant user


    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        # <<< CHANGED: Use HttpRequest in context >>>
        serializer = BookSerializer(instance=self.book_available, context={'request': self.http_request})
        data = serializer.data
        expected_keys = {
            "id", "title", "author", "isbn", "category", "category_display",
            "language", "condition", "condition_display", "available", "image",
            "borrower", "borrower_id", "borrow_date", "due_date", "storage_location",
            "publisher", "publication_year", "copy_number", "added_by", "added_by_id",
            "days_left", "overdue", "days_overdue", "due_today",
            "image_url"
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_field_content_available_book(self):
        """Verify field content for an available book."""
        # <<< CHANGED: Use HttpRequest in context >>>
        serializer = BookSerializer(instance=self.book_available, context={'request': self.http_request})
        data = serializer.data
        self.assertEqual(data['title'], self.book_available.title)
        self.assertEqual(data['isbn'], self.book_available.isbn)
        self.assertEqual(data['category'], 'SF')
        self.assertEqual(data['category_display'], 'Science Fiction')
        self.assertEqual(data['condition'], 'GD')
        self.assertEqual(data['condition_display'], 'Good')
        self.assertTrue(data['available'])
        self.assertIsNone(data['borrower'])
        self.assertIsNone(data['borrower_id'])
        self.assertIsNone(data['borrow_date'])
        self.assertIsNone(data['due_date'])
        self.assertEqual(data['added_by'], self.adder.username)
        self.assertEqual(data['added_by_id'], self.adder.id)
        self.assertIsNone(data['days_left'])
        self.assertFalse(data['overdue'])
        self.assertEqual(data['days_overdue'], 0)
        self.assertFalse(data['due_today'])
        self.assertTrue(data['image_url'].endswith('/static/images/test_cover.jpg'))


    def test_field_content_borrowed_book(self):
        """Verify field content and derived fields for a borrowed (not overdue) book."""
        # <<< CHANGED: Use HttpRequest in context >>>
        serializer = BookSerializer(instance=self.book_borrowed, context={'request': self.http_request})
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['borrower_id'], self.borrower.id)
        self.assertEqual(data['borrow_date'], (date.today() - timedelta(days=5)).isoformat())
        self.assertEqual(data['due_date'], (date.today() + timedelta(days=9)).isoformat())
        self.assertEqual(data['days_left'], 9)
        self.assertFalse(data['overdue'])
        self.assertEqual(data['days_overdue'], 0)
        self.assertFalse(data['due_today'])
        self.assertTrue(data['image_url'].endswith('/static/images/library_seal.jpg'))


    def test_field_content_overdue_book(self):
        """Verify field content and derived fields for an overdue book."""
        # <<< CHANGED: Use HttpRequest in context >>>
        serializer = BookSerializer(instance=self.book_overdue, context={'request': self.http_request})
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['due_date'], (date.today() - timedelta(days=6)).isoformat())
        self.assertEqual(data['days_left'], -6)
        self.assertTrue(data['overdue'])
        self.assertEqual(data['days_overdue'], 6)
        self.assertFalse(data['due_today'])
        self.assertTrue(data['image_url'].endswith('/static/images/library_seal.jpg'))


    def test_field_content_due_today_book(self):
        """Verify field content and derived fields for a book due today."""
        # <<< CHANGED: Use HttpRequest in context >>>
        serializer = BookSerializer(instance=self.book_due_today, context={'request': self.http_request})
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['due_date'], date.today().isoformat())
        self.assertEqual(data['days_left'], 0)
        self.assertFalse(data['overdue'])
        self.assertEqual(data['days_overdue'], 0)
        self.assertTrue(data['due_today'])
        self.assertTrue(data['image_url'].endswith('/static/images/library_seal.jpg'))


    def test_read_only_fields_on_update(self):
        """Verify read-only fields are ignored during update."""
        update_data = {
            "title": "Attempt Update ReadOnly",
            "available": False,
            "borrower": self.borrower.id,
            "borrower_id": self.borrower.id,
            "due_date": date.today().isoformat(),
            "added_by": self.borrower.username,
            "category_display": "Fantasy",
            "days_left": 5,
        }
        book = self.book_available
        # Context might not be needed if not testing URL generation on update
        serializer = BookSerializer(instance=book, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        for field in [
            "available", "borrower", "borrower_id", "due_date", "added_by",
            "category_display", "days_left", "overdue", "days_overdue", "due_today"
        ]:
            self.assertNotIn(field, serializer.validated_data)

        updated_book = serializer.save()
        self.assertEqual(updated_book.title, "Attempt Update ReadOnly")
        self.assertTrue(updated_book.available)
        self.assertIsNone(updated_book.borrower)
        self.assertIsNone(updated_book.due_date)
        self.assertEqual(updated_book.added_by, self.adder)

    def test_create_book_validation_required_fields(self):
        """Test validation fails if required fields are missing on create."""
        required_fields = ["title", "author", "isbn", "category", "language", "condition"]
        for field in required_fields:
            invalid_data = {
                "title": "Test", "author": "Test", "isbn": "9789999999000",
                "category": "SF", "language": "Test", "condition": "GD"
            }
            del invalid_data[field]
            serializer = BookSerializer(data=invalid_data)
            with self.assertRaises(DRFValidationError) as cm:
                serializer.is_valid(raise_exception=True)
            self.assertIn(field, cm.exception.detail, f"Validation error for missing field '{field}' not found.")

    def test_create_book_validation_invalid_choices(self):
        """Test validation fails for invalid category or condition choices."""
        invalid_category_data = {
            "title": "Test", "author": "Test", "isbn": "9789999999001",
            "category": "XX", "language": "Test", "condition": "GD"
        }
        serializer = BookSerializer(data=invalid_category_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('category', cm.exception.detail)

        invalid_condition_data = {
            "title": "Test", "author": "Test", "isbn": "9789999999002",
            "category": "SF", "language": "Test", "condition": "XX"
        }
        serializer = BookSerializer(data=invalid_condition_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('condition', cm.exception.detail)

    def test_create_book_validation_duplicate_isbn(self):
        """Test validation fails if ISBN already exists."""
        invalid_data = {
            "title": "Duplicate ISBN", "author": "Test", "isbn": self.book_available.isbn,
            "category": "SF", "language": "Test", "condition": "GD"
        }
        with self.assertRaises(DjangoValidationError) as cm:
             new_book = Book(**invalid_data)
             new_book.full_clean()
        self.assertIn('isbn', cm.exception.error_dict)