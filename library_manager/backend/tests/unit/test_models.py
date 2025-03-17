from django.test import TestCase
from backend.models import People, Book
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
        user = People.objects.create(name="Test User", numberbooks=3, type="US", age=25) # Added age=25
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.numberbooks, 3)
        self.assertEqual(user.type, "US")
        self.assertEqual(str(user), "Test User")  # Test __str__ method

    def test_user_fields_types(self):
        """
        Test the data types of User model fields.
        """
        user = People.objects.create(name="Field Test User", numberbooks=1, type="AD", age=30) # Added age=30
        self.assertIsInstance(user.id, int)
        self.assertIsInstance(user.name, str)
        self.assertIsInstance(user.numberbooks, int)
        self.assertIsInstance(user.type, str)

    def test_user_type_choices(self):
        """
        Test that User type field enforces choices correctly.
        """
        valid_types = ["AD", "US", "LB"]
        for user_type in valid_types:
            People.objects.create(
                name=f"Valid Type User {user_type}", numberbooks=0, type=user_type, age=35 # Added age=35
            )

        with self.assertRaises(
            ValidationError
        ):  # Expect ValidationError because full_clean is used
            user = People.objects.create(
                name="Invalid Type User", numberbooks=0, type="XX", age=40 # Added age=40
            )  # XX is not a valid choice
            user.full_clean()
            # user.save() # No need to save, validation should fail before save



class BookModelTest(TestCase):
    """
    Test suite for the Book model.
    """

    def setUp(self):
        """
        Set up a user instance for creating book instances.
        """
        self.user = People.objects.create(name="Test User", numberbooks=0, type="US", age=22) # Added age=22

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
            category="MY",
            language="English",
            user=self.user,
            condition="GD",
            available=False,
            storage_location="Shelf Z5", 
            publisher="Test Publisher", 
            publication_year=2023, 
            copy_number=5 
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.due_date, today)
        self.assertEqual(book.isbn, "1234567890123")
        self.assertEqual(book.category, "MY")
        self.assertEqual(book.language, "English")
        self.assertEqual(book.user, self.user)
        self.assertEqual(book.condition, "GD")
        self.assertEqual(book.available, False)
        self.assertEqual(book.storage_location, "Shelf Z5")
        self.assertEqual(book.publisher, "Test Publisher")
        self.assertEqual(book.publication_year, 2023)
        self.assertEqual(book.copy_number, 5)
        self.assertEqual(str(book), "Test Book")  # Test __str__ method

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
            category="CR",
            language="Spanish",
            user=self.user,
            condition="NW",
            available=True,
            storage_location="Shelf Y6", 
            publisher="Another Publisher", 
            publication_year=2024, 
            copy_number=10 
        )
        self.assertIsInstance(book.id, int)
        self.assertIsInstance(book.title, str)
        self.assertIsInstance(book.author, str)
        self.assertIsInstance(book.due_date, date)
        self.assertIsInstance(book.isbn, str)
        self.assertIsInstance(book.category, str)
        self.assertIsInstance(book.language, str)
        self.assertIsInstance(book.user.id, int)  # Foreign key to User
        self.assertIsInstance(book.condition, str)
        self.assertIsInstance(book.available, bool)
        self.assertIsInstance(book.storage_location, str) 
        self.assertIsInstance(book.publisher, str) 
        self.assertIsInstance(book.publication_year, int) 
        self.assertIsInstance(book.copy_number, int) 

    def test_book_category_choices(self):
        """
        Test that Book category field enforces choices correctly.
        """
        valid_categories = ["CK", "CR", "MY", "SF", "FAN", "HIS", "ROM", "TXT"]
        today = date.today()
        for category in valid_categories:
            Book.objects.create(
                title=f"Valid Category Book {category}",
                author="Author",
                due_date=today,
                isbn=f"11111111111{valid_categories.index(category)}",
                category=category,
                language="English",
                user=self.user,
                condition="GD",
                available=True,
                storage_location="Shelf X7", 
                publisher="Yet Another Publisher", 
                publication_year=2021, 
                copy_number=15 
            )

        with self.assertRaises(
            ValidationError
        ):  # Expect ValidationError because full_clean is used
            book = Book(  # Create Book object but don't save yet
                title="Invalid Category Book",
                author="Author",
                due_date=today,
                isbn="1111111111199",
                category="XXX",  # XXX is not a valid choice
                language="English",
                user=self.user,
                condition="GD",
                available=True,
                storage_location="Shelf W8", 
                publisher="Invalid Category Publisher", 
                publication_year=2000, 
                copy_number=20 
            )
            book.full_clean()  # Explicitly call full_clean to trigger validation
            # book.save() # No need to save, validation should fail before save

    def test_book_condition_choices(self):
        """
        Test that Book condition field enforces choices correctly.
        """
        valid_conditions = ["NW", "GD", "FR", "PO"]
        today = date.today()
        for condition in valid_conditions:
            Book.objects.create(
                title=f"Valid Condition Book {condition}",
                author="Author",
                due_date=today,
                isbn=f"22222222222{valid_conditions.index(condition)}",
                category="CK",
                language="English",
                user=self.user,
                condition=condition,
                available=True,
                storage_location="Shelf V9", 
                publisher="Condition Publisher", 
                publication_year=2019, 
                copy_number=25 
            )

        with self.assertRaises(
            ValidationError
        ):  # Expect ValidationError because full_clean is used
            book = Book(
                title="Invalid Condition Book",
                author="Author",
                due_date=today,
                isbn="2222222222299",
                category="CK",
                language="English",
                user=self.user,
                condition="BAD",
                available=True,  # BAD is not a valid choice
                storage_location="Shelf U10", 
                publisher="Invalid Condition Publisher", 
                publication_year=2010, 
                copy_number=30 
            )
            book.full_clean()

    def test_book_isbn_unique(self):
        """
        Test that Book ISBN field is unique and enforces uniqueness.
        """
        today = date.today()
        Book.objects.create(
            title="Book 1",
            author="Author",
            due_date=today,
            isbn="1231231231231",
            category="CK",
            language="English",
            user=self.user,
            condition="NW",
            available=True,
            storage_location="Shelf T11", 
            publisher="Unique ISBN Publisher", 
            publication_year=2005, 
            copy_number=35 
        )
        with self.assertRaises(
            IntegrityError
        ):  # Expecting database integrity error for duplicate ISBN
            Book.objects.create(
                title="Book 2",
                author="Author",
                due_date=today,
                isbn="1231231231231",
                category="CR",
                language="English",  # Same ISBN as Book 1
                user=self.user,
                condition="GD",
                available=True,
                storage_location="Shelf S12", 
                publisher="Duplicate ISBN Publisher", 
                publication_year=2008, 
                copy_number=40 
            )
