from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.validations import validate_username, validate_password, validate_email, validate_birth_date


class UsernameValidationTests(TestCase):

    def test_valid_username(self):
        """Test that a valid username passes validation."""
        validate_username("validUser")  # Should not raise error

    def test_invalid_short_username(self):
        """Test that a username that is too short raises a validation error."""
        with self.assertRaises(ValidationError):
            validate_username("ab")  # Too short, should raise error

    def test_existing_username(self):
        """Test that an existing username raises a validation error."""
        from django.contrib.auth.models import User
        User.objects.create(username="existingUser", password="password123")
        with self.assertRaises(ValidationError):
            validate_username("existingUser")  # Already exists

class PasswordValidationTests(TestCase):

    def test_valid_password(self):
        """Test that a valid password passes validation."""
        validate_password("StrongP@sswOrd1")  # Should not raise error

    def test_invalid_short_password(self):
        """Test that a password that is too short raises a validation error."""
        with self.assertRaises(ValidationError):
            validate_password("123")  # Too short

    def test_invalid_password_no_uppercase(self):
        """Test that a password without an uppercase letter raises a validation error."""
        with self.assertRaises(ValidationError):
            validate_password("password123")  # No uppercase letter

    def test_invalid_password_no_number(self):
        """Test that a password without a number raises a validation error."""
        with self.assertRaises(ValidationError):
            validate_password("Password")  # No number

class EmailValidationTests(TestCase):

    def test_valid_email(self):
        """Test that a valid email passes validation."""
        validate_email("test@example.com")  # Should not raise error

    def test_invalid_email_already_used(self):
        """Test that using an already registered email raises a validation error."""
        from django.contrib.auth.models import User
        User.objects.create(username="testuser", email="test@example.com", password="password123")
        with self.assertRaises(ValidationError):
            # Email already in use
            validate_email("test@example.com")  # Already in use

class BirthDateValidationTests(TestCase): # Added a class for BirthDate
    def test_valid_birth_date(self):
        """Test that a valid birth date passes validation."""
        validate_birth_date("2000-01-01")  # Should not raise error

    def test_invalid_birth_date_format(self):
        """Test that an invalid birth date format raises a validation error."""
        with self.assertRaises(ValidationError):
            validate_birth_date("01-01-2000")  # Wrong format

    def test_invalid_birth_date_underage(self):
        """Test that an underage birth date raises a validation error."""
        with self.assertRaises(ValidationError):
            # User is underage
            validate_birth_date("2015-01-01")  # User is underage