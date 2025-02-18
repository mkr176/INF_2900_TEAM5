from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.validations import validate_username, validate_password, validate_email, validate_birth_date
from django.contrib.auth.models import User

class ValidationTests(TestCase):

    def test_valid_username(self):
        validate_username("validUser")  # Should not raise error

    def test_invalid_short_username(self):
        with self.assertRaises(ValidationError):
            validate_username("ab")  # Too short, should raise error

    def test_existing_username(self):
        User.objects.create(username="existingUser", password="password123")
        with self.assertRaises(ValidationError):
            validate_username("existingUser")  # Already exists

    def test_valid_password(self):
        validate_password("StrongP@ss1")  # Should not raise error

    def test_invalid_short_password(self):
        with self.assertRaises(ValidationError):
            validate_password("123")  # Too short

    def test_invalid_password_no_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_password("password123")  # No uppercase letter

    def test_invalid_password_no_number(self):
        with self.assertRaises(ValidationError):
            validate_password("Password")  # No number

    def test_valid_email(self):
        validate_email("test@example.com")  # Should not raise error

    def test_invalid_email_already_used(self):
        User.objects.create(username="testuser", email="test@example.com", password="password123")
        with self.assertRaises(ValidationError):
            validate_email("test@example.com")  # Already in use

    def test_valid_birth_date(self):
        validate_birth_date("2000-01-01")  # Should not raise error

    def test_invalid_birth_date_format(self):
        with self.assertRaises(ValidationError):
            validate_birth_date("01-01-2000")  # Wrong format

    def test_invalid_birth_date_underage(self):
        with self.assertRaises(ValidationError):
            validate_birth_date("2015-01-01")  # Under 16 years old

