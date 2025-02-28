from django.test import TestCase
from backend.models import User, Book
from django.db import IntegrityError
from datetime import date
from django.core.exceptions import ValidationError

class UserModelTest(TestCase):
    """
    Test suite for the User model.
    """

    def test_user_creation(self):
        """
        Test successful creation of a User instance.
        """
        user = User.objects.create(
            name="Test User",
            numberbooks=3,
            type='US'
        )
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.numberbooks, 3)
        self.assertEqual(user.type, 'US')
        self.assertEqual(str(user), "Test User") # Test __str__ method

    def test_user_fields_types(self):
        """
        Test the data types of User model fields.
        """
        user = User.objects.create(
            name="Field Test User",
            numberbooks=1,
            type='AD'
        )
        self.assertIsInstance(user.id, int)
        self.assertIsInstance(user.name, str)
        self.assertIsInstance(user.numberbooks, int)
        self.assertIsInstance(user.type, str)

    def test_user_type_choices(self):
        """
        Test that User type field enforces choices correctly.
        """
        valid_types = ['AD', 'US', 'LB']
        for user_type in valid_types:
            User.objects.create(name=f"Valid Type User {user_type}", numberbooks=0, type=user_type)

        with self.assertRaises(ValueError):
            User.objects.create(name="Invalid Type User", numberbooks=0, type='XX') # XX is not a valid choice


class BookModelTest(TestCase):
    """
    Test suite for the Book model.
    """

    def setUp(self):
        """
        Set up a user instance for creating book instances.
        """
        self.user = User.objects.create(name="Test User", numberbooks=0, type='US')

    def test_book_creation(self):
        """
        Test successful creation of a Book instance.
        """
        today = date.today()
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            due_date=today,
            isbn="1234567890123",
            category='MY',
            language="English",
            user=self.user,
            condition='GD',
            available=False
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.due_date, today)
        self.assertEqual(book.isbn, "1234567890123")
        self.assertEqual(book.category, 'MY')
        self.assertEqual(book.language, "English")
        self.assertEqual(book.user, self.user)
        self.assertEqual(book.condition, 'GD')
        self.assertEqual(book.available, False)
        self.assertEqual(str(book), "Test Book") # Test __str__ method


    def test_book_fields_types(self):
        """
        Test the data types of Book model fields.
        """
        today = date.today()
        book = Book.objects.create(
            title="Field Test Book",
            author="Test Author",
            due_date=today,
            isbn="9876543210987",
            category='CR',
            language="Spanish",
            user=self.user,
            condition='NW',
            available=True
        )
        self.assertIsInstance(book.id, int)
        self.assertIsInstance(book.title, str)
        self.assertIsInstance(book.author, str)
        self.assertIsInstance(book.due_date, date)
        self.assertIsInstance(book.isbn, str)
        self.assertIsInstance(book.category, str)
        self.assertIsInstance(book.language, str)
        self.assertIsInstance(book.user.id, int) # Foreign key to User
        self.assertIsInstance(book.condition, str)
        self.assertIsInstance(book.available, bool)

    def test_book_category_choices(self):
        """
        Test that Book category field enforces choices correctly.
        """
        valid_categories = ['CK', 'CR', 'MY', 'SF', 'FAN', 'HIS', 'ROM', 'TXT']
        today = date.today()
        for category in valid_categories:
            Book.objects.create(
                title=f"Valid Category Book {category}", author="Author", due_date=today,
                isbn=f"11111111111{valid_categories.index(category)}", category=category, language="English",
                user=self.user, condition='GD', available=True
            )

        with self.assertRaises(ValidationError): # Expect ValidationError because full_clean is used
            book = Book( # Create Book object but don't save yet
                title="Invalid Category Book",
                author="Author",
                due_date=today,
                isbn="1111111111199",
                category='XXX', # XXX is not a valid choice
                language="English",
                user=self.user,
                condition='GD',
                available=True
            )
            book.full_clean() # Explicitly call full_clean to trigger validation
            # book.save() # No need to save, validation should fail before save


    def test_book_condition_choices(self):
        """
        Test that Book condition field enforces choices correctly.
        """
        valid_conditions = ['NW', 'GD', 'FR', 'PO']
        today = date.today()
        for condition in valid_conditions:
            Book.objects.create(
                title=f"Valid Condition Book {condition}", author="Author", due_date=today,
                isbn=f"22222222222{valid_conditions.index(condition)}", category='CK', language="English",
                user=self.user, condition=condition, available=True
            )

        with self.assertRaises(ValueError):
            Book.objects.create(
                title="Invalid Condition Book", author="Author", due_date=today,
                isbn="2222222222299", category='CK', language="English",
                user=self.user, condition='BAD', available=True # BAD is not a valid choice
            )

    def test_book_isbn_unique(self):
        """
        Test that Book ISBN field is unique and enforces uniqueness.
        """
        today = date.today()
        Book.objects.create(
            title="Book 1", author="Author", due_date=today,
            isbn="1231231231231", category='CK', language="English",
            user=self.user, condition='NW', available=True
        )
        with self.assertRaises(IntegrityError): # Expecting database integrity error for duplicate ISBN
            Book.objects.create(
                title="Book 2", author="Author", due_date=today,
                isbn="1231231231231", category='CR', language="English", # Same ISBN as Book 1
                user=self.user, condition='GD', available=True
            )