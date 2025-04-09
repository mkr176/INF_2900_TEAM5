import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from backend.models import UserProfile, Book

# Get the User model
User = get_user_model()

# Mark all tests in this module to use the database
pytestmark = pytest.mark.django_db

# --- UserProfile Model Tests ---

class UserProfileModelTests(TestCase):
    """Tests for the UserProfile model."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        # UserProfile is automatically created via a signal or needs manual creation?
        # Assuming manual creation is needed if no signal exists.
        # If a signal creates it, this might raise an IntegrityError or we fetch the existing one.
        # Let's assume manual creation for now, adjust if needed based on actual implementation.
        try:
            cls.profile = UserProfile.objects.create(
                user=cls.user,
                type='US',
                age=30
            )
        except IntegrityError: # Handle case where profile might be auto-created
             cls.profile = UserProfile.objects.get(user=cls.user)


    def test_user_profile_creation(self):
        """Test that a UserProfile is linked correctly to a User."""
        self.assertEqual(UserProfile.objects.count(), 1)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.pk, self.user.pk) # Check if user_id is the primary key

    def test_user_profile_default_type(self):
        """Test the default type for a new UserProfile."""
        user2 = User.objects.create_user(username='testuser2', password='password123')
        # Assuming manual creation or fetching if auto-created
        try:
            profile2 = UserProfile.objects.create(user=user2)
        except IntegrityError:
            profile2 = UserProfile.objects.get(user=user2)
        self.assertEqual(profile2.type, 'US') # Default should be 'User'

    def test_user_profile_type_choices(self):
        """Test the choices for the type field."""
        self.profile.type = 'AD'
        self.profile.save()
        self.assertEqual(self.profile.get_type_display(), 'Admin')

        self.profile.type = 'LB'
        self.profile.save()
        self.assertEqual(self.profile.get_type_display(), 'Librarian')

        # Test invalid choice
        with self.assertRaises(ValidationError):
             # Direct assignment might bypass validation depending on Django version/setup
             # A full_clean() call is often needed to trigger model validation
             self.profile.type = 'INVALID'
             self.profile.full_clean()


    def test_user_profile_str_representation(self):
        """Test the __str__ method of UserProfile."""
        expected_str = f"{self.user.username}'s Profile ({self.profile.get_type_display()})"
        self.assertEqual(str(self.profile), expected_str)

    def test_user_profile_on_delete_cascade(self):
        """Test that deleting the User also deletes the UserProfile."""
        user_id = self.user.id
        self.user.delete()
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(user_id=user_id)


# --- Book Model Tests ---

class BookModelTests(TestCase):
    """Tests for the Book model."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user1 = User.objects.create_user(username='librarian', password='password123')
        UserProfile.objects.create(user=cls.user1, type='LB') # Create profile for user

        cls.user2 = User.objects.create_user(username='borrower', password='password123')
        UserProfile.objects.create(user=cls.user2, type='US') # Create profile for user

        cls.book = Book.objects.create(
            title="Test Book One",
            author="Test Author",
            isbn="9780000000001",
            category="SF",
            language="English",
            added_by=cls.user1,
            condition='GD',
            publisher="Test Publisher",
            publication_year=2023
        )

    def test_book_creation(self):
        """Test creating a Book instance."""
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.get(isbn="9780000000001")
        self.assertEqual(book.title, "Test Book One")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.added_by, self.user1)
        self.assertEqual(book.category, "SF")
        self.assertEqual(book.get_category_display(), "Science Fiction") # Check display name
        self.assertEqual(book.condition, "GD")
        self.assertEqual(book.get_condition_display(), "Good") # Check display name

    def test_book_default_values(self):
        """Test the default values for a new Book."""
        self.assertTrue(self.book.available)
        self.assertIsNone(self.book.borrower)
        self.assertIsNone(self.book.borrow_date)
        self.assertIsNone(self.book.due_date)
        # Check default image path if applicable (requires setup for media files in tests)
        # self.assertEqual(self.book.image.name, 'static/images/library_seal.jpg')

    def test_book_str_representation(self):
        """Test the __str__ method of Book."""
        self.assertEqual(str(self.book), "Test Book One")

    def test_book_isbn_uniqueness(self):
        """Test the unique constraint on the ISBN field."""
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Test Book Two",
                author="Another Author",
                isbn="9780000000001", # Same ISBN as self.book
                category="FAN",
                language="English",
                added_by=self.user1,
                condition='NW'
            )

    def test_book_category_choices(self):
        """Test the choices for the category field."""
        self.book.category = 'HIS'
        self.book.save()
        self.assertEqual(self.book.get_category_display(), 'History')

        # Test invalid choice
        with self.assertRaises(ValidationError):
             self.book.category = 'INVALID'
             self.book.full_clean() # Trigger validation

    def test_book_condition_choices(self):
        """Test the choices for the condition field."""
        self.book.condition = 'PO'
        self.book.save()
        self.assertEqual(self.book.get_condition_display(), 'Poor')

        # Test invalid choice
        with self.assertRaises(ValidationError):
             self.book.condition = 'INVALID'
             self.book.full_clean() # Trigger validation

    def test_book_added_by_on_delete_set_null(self):
        """Test on_delete=SET_NULL for the added_by field."""
        book_id = self.book.id
        self.user1.delete() # Delete the user who added the book
        book = Book.objects.get(id=book_id)
        self.assertIsNone(book.added_by) # added_by should be set to NULL

    def test_book_borrower_on_delete_set_null(self):
        """Test on_delete=SET_NULL for the borrower field."""
        # Assign a borrower first
        self.book.borrower = self.user2
        self.book.available = False
        self.book.save()

        book_id = self.book.id
        borrower_id = self.user2.id
        self.user2.delete() # Delete the borrower

        book = Book.objects.get(id=book_id)
        self.assertIsNone(book.borrower) # borrower should be set to NULL
        # Optional: Check if the book becomes available again upon borrower deletion (depends on requirements)
        # self.assertTrue(book.available) # This depends on desired logic