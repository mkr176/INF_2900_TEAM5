from django.test import TestCase
from backend.models import People, Book
from django.db import IntegrityError
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone  # Use timezone for consistency if needed


class UserModelTest(TestCase):
    """
    Test suite for the People model.
    """

    # Suggestion 1: Use setUpTestData for efficiency if data doesn't change per test
    # Or setUp if modifications are needed per test method
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "name": "Test User",
            "numberbooks": 3,
            "type": "US",
            "age": 25,
            "email": "test@example.com",  # Added email for completeness
            "password": "password123",  # Added password for completeness
        }
        cls.user = People.objects.create(**cls.user_data)

    def test_user_creation(self):
        """
        Test successful creation of a People instance.
        """
        self.assertEqual(self.user.name, self.user_data["name"])
        self.assertEqual(self.user.numberbooks, self.user_data["numberbooks"])
        self.assertEqual(self.user.type, self.user_data["type"])
        self.assertEqual(self.user.age, self.user_data["age"])
        self.assertEqual(self.user.email, self.user_data["email"])
        # Avoid testing plain text password storage directly if possible
        # self.assertEqual(self.user.password, self.user_data["password"])
        self.assertEqual(str(self.user), self.user_data["name"])  # Test __str__ method

    def test_user_fields_types(self):
        """
        Test the data types of People model fields.
        """
        # User created in setUpTestData
        self.assertIsInstance(self.user.id, int)
        self.assertIsInstance(self.user.name, str)
        self.assertIsInstance(self.user.numberbooks, int)
        self.assertIsInstance(self.user.type, str)
        self.assertIsInstance(self.user.age, int)
        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.password, str)

    def test_user_type_choices_valid(self):
        """
        Test that User type field accepts valid choices.
        """
        valid_types = ["AD", "US", "LB"]
        for i, user_type in enumerate(valid_types):
            # Use different names/emails to avoid potential unique constraints if added later
            People.objects.create(
                name=f"Valid Type User {user_type}_{i}",
                numberbooks=0,
                type=user_type,
                age=35 + i,
                email=f"valid_{i}@example.com",
            )
        # Check count if needed
        self.assertEqual(
            People.objects.count(), 1 + len(valid_types)
        )  # 1 from setUpTestData

    def test_user_type_choices_invalid(self):
        """
        Test that User type field rejects invalid choices during validation.
        """
        with self.assertRaises(ValidationError):
            # Create an instance but don't save yet
            invalid_user = People(
                name="Invalid Type User",
                numberbooks=0,
                type="XX",  # XX is not a valid choice
                age=40,
                email="invalid@example.com",
            )
            # Explicitly call full_clean to trigger model validation
            invalid_user.full_clean()
            # No need to save, validation should fail before save


class BookModelTest(TestCase):
    """
    Test suite for the Book model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up a user instance and today's date for creating book instances.
        """
        cls.user = People.objects.create(
            name="Test User",
            numberbooks=0,
            type="US",
            age=22,
            email="bookuser@example.com",
        )
        # Suggestion 2: Define today in setUpTestData
        cls.today = date.today()
        # Suggestion 3: Define default book data
        cls.default_book_data = {
            "title": "Default Book Title",
            "author": "Default Author",
            "due_date": cls.today,
            "isbn": "1111111111111",
            "category": "MY",
            "language": "English",
            "user": cls.user,
            "condition": "GD",
            "available": True,
            "storage_location": "Shelf A1",
            "publisher": "Default Publisher",
            "publication_year": 2022,
            "copy_number": 1,
        }

    # Suggestion 3: Helper method to create books
    def _create_book(self, **kwargs):
        """Helper method to create a book instance with overrides."""
        data = self.default_book_data.copy()
        data.update(kwargs)
        # Ensure ISBN is unique for each creation if not provided
        if "isbn" not in kwargs:
            # Generate a unique ISBN based on current count or timestamp
            timestamp_isbn = str(timezone.now().timestamp()).replace(".", "")[:13]
            data["isbn"] = timestamp_isbn.ljust(13, "0")  # Pad if needed
            # Or use Book.objects.count() + some base number if preferred and reliable
            # data['isbn'] = f"978000000000{Book.objects.count() + 1}"[-13:]

        # Handle potential user override
        if "user" in kwargs and kwargs["user"] is None:
            data["user"] = None  # Allow setting user to None if explicitly passed
        elif "user" not in kwargs:
            data["user"] = self.user  # Default to the test user if not specified

        return Book.objects.create(**data)

    def test_book_creation(self):
        """
        Test successful creation of a Book instance using helper.
        """
        book_data = {
            "title": "Test Book Creation",
            "author": "Test Author",
            "isbn": "1234567890123",  # Specific ISBN for this test
            "category": "SF",
            "available": False,
            "copy_number": 5,
        }
        book = self._create_book(**book_data)

        self.assertEqual(book.title, book_data["title"])
        self.assertEqual(book.author, book_data["author"])
        self.assertEqual(book.due_date, self.today)  # From default data
        self.assertEqual(book.isbn, book_data["isbn"])
        self.assertEqual(book.category, book_data["category"])
        self.assertEqual(
            book.language, self.default_book_data["language"]
        )  # From default
        self.assertEqual(book.user, self.user)  # From default
        self.assertEqual(
            book.condition, self.default_book_data["condition"]
        )  # From default
        self.assertEqual(book.available, book_data["available"])
        self.assertEqual(
            book.storage_location, self.default_book_data["storage_location"]
        )
        self.assertEqual(book.publisher, self.default_book_data["publisher"])
        self.assertEqual(
            book.publication_year, self.default_book_data["publication_year"]
        )
        self.assertEqual(book.copy_number, book_data["copy_number"])
        self.assertEqual(str(book), book_data["title"])  # Test __str__ method

    def test_book_fields_types(self):
        """
        Test the data types of Book model fields using helper.
        """
        # Create a book using the helper with a unique ISBN for this test
        book = self._create_book(isbn="9876543210987")

        self.assertIsInstance(book.id, int)
        self.assertIsInstance(book.title, str)
        self.assertIsInstance(book.author, str)
        # Allow due_date to be None as per model definition (null=True, blank=True)
        self.assertTrue(isinstance(book.due_date, date) or book.due_date is None)
        self.assertIsInstance(book.isbn, str)
        self.assertIsInstance(book.category, str)
        self.assertIsInstance(book.language, str)
        # Allow user to be None as per model definition (null=True, blank=True)
        self.assertTrue(isinstance(book.user, People) or book.user is None)
        if book.user:  # Check user.id only if user is not None
            self.assertIsInstance(book.user.id, int)
        self.assertIsInstance(book.condition, str)
        self.assertIsInstance(book.available, bool)
        # Allow optional fields to be None
        self.assertTrue(
            isinstance(book.storage_location, str) or book.storage_location is None
        )
        self.assertTrue(isinstance(book.publisher, str) or book.publisher is None)
        self.assertTrue(
            isinstance(book.publication_year, int) or book.publication_year is None
        )
        self.assertTrue(isinstance(book.copy_number, int) or book.copy_number is None)
        # Allow borrower to be None
        self.assertTrue(isinstance(book.borrower, People) or book.borrower is None)
        if book.borrower:
            self.assertIsInstance(book.borrower.id, int)
        # Allow borrow_date to be None
        self.assertTrue(isinstance(book.borrow_date, date) or book.borrow_date is None)

    def test_book_category_choices_valid(self):
        """
        Test that Book category field accepts valid choices.
        """
        valid_categories = ["CK", "CR", "MY", "SF", "FAN", "HIS", "ROM", "TXT"]
        initial_book_count = Book.objects.count()
        for i, category in enumerate(valid_categories):
            # Use helper, provide unique ISBN and the category
            self._create_book(
                title=f"Valid Category Book {category}",
                isbn=f"333{i:010d}",  # Generate unique ISBNs
                category=category,
            )
        self.assertEqual(
            Book.objects.count(), initial_book_count + len(valid_categories)
        )

    def test_book_category_choices_invalid(self):
        """
        Test that Book category field rejects invalid choices during validation.
        """
        with self.assertRaises(ValidationError):
            # Use helper to get default data, then modify category before full_clean
            invalid_data = self.default_book_data.copy()
            invalid_data["category"] = "XXX"  # Invalid choice
            invalid_data["isbn"] = "4440000000000"  # Unique ISBN
            # Need to handle the user ForeignKey correctly when creating instance directly
            invalid_data["user"] = self.user

            book = Book(**invalid_data)
            book.full_clean()  # Explicitly call full_clean

    def test_book_condition_choices_valid(self):
        """
        Test that Book condition field accepts valid choices.
        """
        valid_conditions = ["NW", "GD", "FR", "PO"]
        initial_book_count = Book.objects.count()
        for i, condition in enumerate(valid_conditions):
            self._create_book(
                title=f"Valid Condition Book {condition}",
                isbn=f"555{i:010d}",  # Generate unique ISBNs
                condition=condition,
            )
        self.assertEqual(
            Book.objects.count(), initial_book_count + len(valid_conditions)
        )

    def test_book_condition_choices_invalid(self):
        """
        Test that Book condition field rejects invalid choices during validation.
        """
        with self.assertRaises(ValidationError):
            invalid_data = self.default_book_data.copy()
            invalid_data["condition"] = "BAD"  # Invalid choice
            invalid_data["isbn"] = "6660000000000"  # Unique ISBN
            invalid_data["user"] = self.user

            book = Book(**invalid_data)
            book.full_clean()

    def test_book_isbn_unique(self):
        """
        Test that Book ISBN field enforces uniqueness at the database level.
        """
        unique_isbn = "7777777777777"
        # Create the first book using the helper
        self._create_book(isbn=unique_isbn, title="Book 1")

        # Attempt to create a second book with the same ISBN
        with self.assertRaises(IntegrityError):
            self._create_book(isbn=unique_isbn, title="Book 2")

    def test_book_optional_fields_can_be_null(self):
        """
        Test that fields allowing null/blank can be saved as such.
        """
        isbn = "8888888888888"
        book = self._create_book(
            isbn=isbn,
            due_date=None,
            user=None,  # Explicitly set user to None
            borrower=None,
            borrow_date=None,
            storage_location=None,
            publisher=None,
            publication_year=None,
            copy_number=None,
        )
        # Refresh from DB to be sure
        book.refresh_from_db()
        self.assertIsNone(book.due_date)
        self.assertIsNone(book.user)
        self.assertIsNone(book.borrower)
        self.assertIsNone(book.borrow_date)
        self.assertIsNone(book.storage_location)
        self.assertIsNone(book.publisher)
        self.assertIsNone(book.publication_year)
        self.assertIsNone(book.copy_number)

    def test_book_image_default(self):
        """
        Test that the image field has the correct default value.
        """
        book = self._create_book(isbn="9999999999999")
        # Check the name/path of the default image field
        # Note: This checks the string representation stored in the DB,
        # not the actual file existence unless specifically needed.
        self.assertEqual(book.image.name, "static/images/library_seal.jpg")
