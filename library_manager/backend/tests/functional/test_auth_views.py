# -*- coding: utf-8 -*-
"""
Functional tests for Authentication related API views (Register, Login, Logout).
"""
from django.contrib.auth import get_user_model, SESSION_KEY
from rest_framework import status

# Import the base test case
from .test_views_base import LibraryAPITestCaseBase, USER_TYPE

# Get the User model
User = get_user_model()

class AuthViewsTestCase(LibraryAPITestCaseBase):
    """
    Tests for authentication views: Register, Login, Logout.
    Inherits setup from LibraryAPITestCaseBase.
    """

    # --- Test Authentication Views (Register, Login, Logout) ---

    def test_register_user_success(self):
        """Verify a new user can be created successfully."""
        initial_user_count = User.objects.count()
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123',
            'first_name': 'New',
            'last_name': 'User',
            'age': 28,
            'type': USER_TYPE # Explicitly set type or test default
        }
        response = self.client.post(self.register_url, data)
        # print(response.content) # Debugging: print response content if needed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.check_password('StrongPassword123'))
        self.assertEqual(new_user.email, 'new@example.com')
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.age, 28)
        self.assertEqual(new_user.profile.type, USER_TYPE)

    def test_register_user_duplicate_username(self):
        """Attempt registration with an existing username."""
        data = {
            'username': self.user1.username, # Existing username
            'email': 'unique@example.com',
            'password': 'aVeryStrongPassword123!', # Changed password
            'password2': 'aVeryStrongPassword123!', # Changed password
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data) # Check if error is related to username

    def test_register_user_duplicate_email(self):
        """Attempt registration with an existing email."""
        data = {
            'username': 'anothernewuser',
            'email': self.user1.email, # Existing email
            'password': 'aVeryStrongPassword123!', # Changed password
            'password2': 'aVeryStrongPassword123!', # Changed password
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data) # Check if error is related to email

    def test_register_user_password_mismatch(self):
        """Attempt registration with mismatching passwords."""
        data = {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'password123',
            'password2': 'password456', # Mismatch
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data) # Check if error is related to password

    def test_register_user_missing_fields(self):
        """Attempt registration without required fields."""
        # Missing username
        data_no_user = {'email': 'a@b.com', 'password': 'pw', 'password2': 'pw'}
        response = self.client.post(self.register_url, data_no_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

        # Missing email
        data_no_email = {'username': 'a', 'password': 'pw', 'password2': 'pw'}
        response = self.client.post(self.register_url, data_no_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

        # Missing password
        data_no_pw = {'username': 'a', 'email': 'a@b.com', 'password2': 'pw'}
        response = self.client.post(self.register_url, data_no_pw)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_user_weak_password(self):
        """Attempt registration with a password failing validation (basic check)."""
        # This test assumes default validators are active.
        # A very short password might trigger MinimumLengthValidator.
        data = {
            'username': 'weakpwuser',
            'email': 'weak@example.com',
            'password': 'pw', # Too short
            'password2': 'pw',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data) # Expecting validation error on password

    def test_login_user_success(self):
        """Attempt login with correct credentials."""
        login_data = {'username': self.user1.username, 'password': 'password123'}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data) # Check if user data is returned
        self.assertEqual(response.data['username'], self.user1.username)
        # Check if session is authenticated
        self.assertTrue(SESSION_KEY in self.client.session)
        self.assertEqual(str(self.client.session[SESSION_KEY]), str(self.user1.pk))

    def test_login_user_invalid_password(self):
        """Attempt login with incorrect password."""
        login_data = {'username': self.user1.username, 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertNotIn(SESSION_KEY, self.client.session) # Ensure not logged in

    def test_login_user_nonexistent_user(self):
        """Attempt login with a non-existent username."""
        login_data = {'username': 'nosuchuser', 'password': 'password123'}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_login_user_missing_credentials(self):
        """Attempt login without username or password."""
        # Missing password
        response = self.client.post(self.login_url, {'username': self.user1.username})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertNotIn(SESSION_KEY, self.client.session)

        # Missing username
        response = self.client.post(self.login_url, {'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_logout_user_success(self):
        """Log in a user and then log them out."""
        # First, log in using the helper from the base class
        self._login_user('user1')
        self.assertTrue(SESSION_KEY in self.client.session)

        # Then, log out
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        # Check session is now unauthenticated
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_logout_user_unauthenticated(self):
        """Attempt logout without being logged in."""
        response = self.client.post(self.logout_url)
        # DRF defaults usually return 403 Forbidden if authentication fails for IsAuthenticated
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)