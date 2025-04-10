# -*- coding: utf-8 -*-
"""
Unit tests for backend serializers.
"""
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError # For model validation
from rest_framework.exceptions import ValidationError as DRFValidationError # For serializer validation

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
        cls.serializer = UserProfileSerializer(instance=cls.profile)

    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        data = self.serializer.data
        expected_keys = {
            "user_id", "username", "type", "age", "avatar", "get_type_display"
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
        # Assuming default avatar path structure
        self.assertTrue(data['avatar'].endswith('avatars/default.svg'))

    def test_read_only_fields(self):
        """Verify read-only fields cannot be updated via the serializer."""
        update_data = {
            "username": "newusername", # Read-only derived field
            "user_id": self.user.id + 1, # Read-only derived field
            "get_type_display": "Admin", # Read-only method field
            "type": "AD", # Writable field
            "age": 40,    # Writable field
        }
        serializer = UserProfileSerializer(instance=self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        # Check that read-only fields in validated_data are ignored
        self.assertNotIn('username', serializer.validated_data)
        self.assertNotIn('user_id', serializer.validated_data)
        self.assertNotIn('get_type_display', serializer.validated_data)
        # Check that writable fields are present
        self.assertIn('type', serializer.validated_data)
        self.assertIn('age', serializer.validated_data)

        # Save and check instance
        profile = serializer.save()
        self.assertEqual(profile.user.username, "profiletestuser") # Original username
        self.assertEqual(profile.type, "AD") # Updated type
        self.assertEqual(profile.age, 40) # Updated age


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
        cls.serializer = UserSerializer(instance=cls.user)

    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        data = self.serializer.data
        expected_keys = {
            "id", "username", "email", "first_name", "last_name",
            "profile", "date_joined", "is_staff"
        }
        self.assertEqual(set(data.keys()), expected_keys)
        # Ensure password is NOT included
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
        self.assertFalse(data['is_staff']) # Default for create_user

    def test_nested_profile_serialization(self):
        """Verify the nested profile data is serialized correctly."""
        data = self.serializer.data
        self.assertIn('profile', data)
        profile_data = data['profile']
        self.assertIsInstance(profile_data, dict)
        # Check some profile fields within the nested structure
        self.assertEqual(profile_data['user_id'], self.user.id)
        self.assertEqual(profile_data['username'], self.user.username)
        self.assertEqual(profile_data['type'], 'US')
        self.assertEqual(profile_data['age'], 29)

    def test_update_user(self):
        """Verify the serializer can update user fields (excluding password)."""
        update_data = {
            "first_name": "UpdatedFirst",
            "email": "updated@test.com"
        }
        serializer = UserSerializer(instance=self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "UpdatedFirst")
        self.assertEqual(updated_user.email, "updated@test.com")
        # Ensure other fields remain unchanged
        self.assertEqual(updated_user.username, self.user.username)

    def test_password_is_write_only(self):
        """Verify password field is write-only."""
        update_data = {"password": "newpassword123"}
        serializer = UserSerializer(instance=self.user, data=update_data, partial=True)
        # Password is not required for update, so it should be valid
        self.assertTrue(serializer.is_valid(raise_exception=True))
        # Password should NOT be in validated_data because it's write_only
        # Password should NOT be in the serialized output data
        self.assertNotIn('password', serializer.data)

        # Note: The UserSerializer itself doesn't hash the password on save.
        # This is typically handled in the view (like CurrentUserUpdateView).
        # If we called serializer.save() here, the password wouldn't be hashed.


# --- RegisterSerializer Tests ---

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

        # Verify profile creation
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
            # No 'type' provided
        }
        serializer = RegisterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.type, 'US') # Check default

    def test_password_mismatch(self):
        """Test registration fails if passwords do not match."""
        invalid_data = {
            "username": "pwmissmatch",
            "email": "pwmiss@example.com",
            "password": "ValidPassword123",
            "password2": "DifferentPassword123", # Mismatch
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', cm.exception.detail)
        self.assertIn("didn't match", str(cm.exception.detail['password'][0]).lower())

    def test_duplicate_username(self):
        """Test registration fails with a duplicate username."""
        existing_user = UserFactory(username="existinguser")
        invalid_data = {
            "username": "existinguser", # Duplicate
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
        existing_user = UserFactory(username="uniqueuser", email="existing@example.com")
        invalid_data = {
            "username": "anotheruniqueuser",
            "email": "existing@example.com", # Duplicate
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
            del invalid_data[field] # Remove one required field
            serializer = RegisterSerializer(data=invalid_data)
            with self.assertRaises(DRFValidationError) as cm:
                serializer.is_valid(raise_exception=True)
            self.assertIn(field, cm.exception.detail, f"Validation error for missing field '{field}' not found.")

    def test_weak_password(self):
        """Test registration fails with a weak password (e.g., too short)."""
        # Assumes default Django password validators are active
        invalid_data = {
            "username": "weakpwuser",
            "email": "weak@example.com",
            "password": "pw", # Too short
            "password2": "pw",
        }
        serializer = RegisterSerializer(data=invalid_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', cm.exception.detail)
        # Check for a message indicating length issue (might vary based on validator)
        self.assertTrue(any("too short" in str(e).lower() or "minimum length" in str(e).lower() for e in cm.exception.detail['password']))

    def test_invalid_profile_type_choice(self):
        """Test registration fails with an invalid choice for profile type."""
        invalid_data = {
            "username": "invalidtypeuser",
            "email": "invalidtype@example.com",
            "password": "ValidPassword123",
            "password2": "ValidPassword123",
            "type": "XX", # Invalid choice
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
        cls.borrower = UserFactory(username="bookborrower")
        cls.book_available = BookFactory(
            title="Available Book", isbn="9781111111111", category="SF", condition="GD",
            added_by=cls.adder, available=True, borrower=None, borrow_date=None, due_date=None
        )
        cls.book_borrowed = BookFactory(
            title="Borrowed Book", isbn="9782222222222", category="HIS", condition="FR",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9) # Due in 9 days
        )
        cls.book_overdue = BookFactory(
            title="Overdue Book", isbn="9783333333333", category="FAN", condition="PO",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6) # Was due 6 days ago
        )
        cls.book_due_today = BookFactory(
            title="Due Today Book", isbn="9784444444444", category="ROM", condition="NW",
            added_by=cls.adder, available=False, borrower=cls.borrower,
            borrow_date=date.today() - timedelta(days=14),
            due_date=date.today() # Due today
        )

    def test_contains_expected_fields(self):
        """Verify the serializer outputs the expected fields."""
        serializer = BookSerializer(instance=self.book_available)
        data = serializer.data
        expected_keys = {
            "id", "title", "author", "isbn", "category", "category_display",
            "language", "condition", "condition_display", "available", "image",
            "borrower", "borrower_id", "borrow_date", "due_date", "storage_location",
            "publisher", "publication_year", "copy_number", "added_by", "added_by_id",
            "days_left", "overdue", "days_overdue", "due_today",
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_field_content_available_book(self):
        """Verify field content for an available book."""
        serializer = BookSerializer(instance=self.book_available)
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
        # Derived fields for available book
        self.assertIsNone(data['days_left'])
        self.assertFalse(data['overdue'])
        self.assertEqual(data['days_overdue'], 0)
        self.assertFalse(data['due_today'])

    def test_field_content_borrowed_book(self):
        """Verify field content and derived fields for a borrowed (not overdue) book."""
        serializer = BookSerializer(instance=self.book_borrowed)
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['borrower_id'], self.borrower.id)
        self.assertEqual(data['borrow_date'], (date.today() - timedelta(days=5)).isoformat())
        self.assertEqual(data['due_date'], (date.today() + timedelta(days=9)).isoformat())
        # Derived fields
        self.assertEqual(data['days_left'], 9)
        self.assertFalse(data['overdue'])
        self.assertEqual(data['days_overdue'], 0)
        self.assertFalse(data['due_today'])

    def test_field_content_overdue_book(self):
        """Verify field content and derived fields for an overdue book."""
        serializer = BookSerializer(instance=self.book_overdue)
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['due_date'], (date.today() - timedelta(days=6)).isoformat())
        # Derived fields
        self.assertEqual(data['days_left'], -6)
        self.assertTrue(data['overdue'])
        self.assertEqual(data['days_overdue'], 6)
        self.assertFalse(data['due_today'])

    def test_field_content_due_today_book(self):
        """Verify field content and derived fields for a book due today."""
        serializer = BookSerializer(instance=self.book_due_today)
        data = serializer.data
        self.assertFalse(data['available'])
        self.assertEqual(data['borrower'], self.borrower.username)
        self.assertEqual(data['due_date'], date.today().isoformat())
        # Derived fields
        self.assertEqual(data['days_left'], 0)
        self.assertFalse(data['overdue']) # Not overdue yet
        self.assertEqual(data['days_overdue'], 0)
        self.assertTrue(data['due_today'])

    def test_read_only_fields_on_update(self):
        """Verify read-only fields are ignored during update."""
        update_data = {
            "title": "Attempt Update ReadOnly",
            "available": False, # Read-only
            "borrower": self.borrower.id, # Read-only (should be username string anyway)
            "borrower_id": self.borrower.id, # Read-only
            "due_date": date.today().isoformat(), # Read-only
            "added_by": self.borrower.username, # Read-only
            "category_display": "Fantasy", # Read-only
            "days_left": 5, # Read-only
        }
        # Start with an available book
        book = self.book_available
        serializer = BookSerializer(instance=book, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        # Check validated_data excludes read-only fields
        for field in [
            "available", "borrower", "borrower_id", "due_date", "added_by",
            "category_display", "days_left", "overdue", "days_overdue", "due_today"
        ]:
            self.assertNotIn(field, serializer.validated_data)

        # Save and check instance
        updated_book = serializer.save()
        self.assertEqual(updated_book.title, "Attempt Update ReadOnly") # Title updated
        # Verify read-only fields remain unchanged
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
            "category": "XX", "language": "Test", "condition": "GD" # Invalid category
        }
        serializer = BookSerializer(data=invalid_category_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('category', cm.exception.detail)

        invalid_condition_data = {
            "title": "Test", "author": "Test", "isbn": "9789999999002",
            "category": "SF", "language": "Test", "condition": "XX" # Invalid condition
        }
        serializer = BookSerializer(data=invalid_condition_data)
        with self.assertRaises(DRFValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('condition', cm.exception.detail)

    def test_create_book_validation_duplicate_isbn(self):
        """Test validation fails if ISBN already exists."""
        # self.book_available already exists with ISBN "9781111111111"
        invalid_data = {
            "title": "Duplicate ISBN", "author": "Test", "isbn": self.book_available.isbn,
            "category": "SF", "language": "Test", "condition": "GD"
        }
        # Need to use model's full_clean or rely on DB integrity for unique check usually.
        # Serializer validation for uniqueness often requires access to the queryset.
        # Let's test the model validation directly for simplicity here.
        with self.assertRaises(DjangoValidationError) as cm:
             # Create a new book instance and call full_clean
             new_book = Book(**invalid_data)
             new_book.full_clean() # This should raise ValidationError due to unique constraint
        self.assertIn('isbn', cm.exception.error_dict)

        # Note: A serializer-level unique validation would typically look like:
        # serializer = BookSerializer(data=invalid_data)
        # with self.assertRaises(DRFValidationError) as cm:
        #     serializer.is_valid(raise_exception=True)
        # self.assertIn('isbn', cm.exception.detail)
        # This requires the serializer to implement a uniqueness check if not relying solely on the DB.
        # The default ModelSerializer doesn't automatically add this for non-PK unique fields without explicit validators.