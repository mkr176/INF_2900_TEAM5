# -*- coding: utf-8 -*-
"""
Unit tests for backend API views.
Focuses on testing view logic in isolation using mocks.
"""
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock, ANY # ANY is useful for asserting calls with dynamic args

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.urls import reverse # Although not strictly used for requests, can be useful for context
from rest_framework import status
from rest_framework.request import Request as DRFRequest # To wrap factory requests

# Import views, models, serializers, permissions
from backend import views, models, serializers
from backend.views import (
    RegisterView, LoginView, LogoutView, UserListView, CurrentUserView,
    UserDetailView, CurrentUserUpdateView, BookListCreateView, BookDetailView,
    BorrowBookView, ReturnBookView, BorrowedBooksListView, csrf_token_view,
    MAX_BORROW_LIMIT
)
from backend.models import UserProfile, Book
from backend.serializers import (
    UserSerializer, RegisterSerializer, BookSerializer, UserProfileSerializer
)

# Import factories
from ..factories import UserFactory, UserProfileFactory, BookFactory

User = get_user_model()

# --- Test Setup Helper ---

class ViewTestBase(TestCase):
    """Base class with RequestFactory and common setup."""
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        # Create users with different roles
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory(username='testuser_unit')
        UserProfileFactory(user=self.regular_user, type='US')
        self.librarian_user = UserFactory(username='testlibrarian_unit')
        UserProfileFactory(user=self.librarian_user, type='LB')
        self.admin_user = UserFactory(username='testadmin_unit')
        UserProfileFactory(user=self.admin_user, type='AD')

    def _create_drf_request(self, method='get', path='/fake-path/', user=None, data=None, format='json'):
        """Creates a DRF Request object wrapped around a RequestFactory request."""
        user = user or self.anonymous_user
        factory_method = getattr(self.factory, method)
        # For POST/PUT/PATCH etc., pass data; for GET, pass data as query params
        if method.lower() in ['post', 'put', 'patch', 'delete']:
            request = factory_method(path, data=data, content_type=f'application/{format}')
        else:
            request = factory_method(path, data=data) # GET data becomes query params

        request.user = user
        # Wrap with DRF Request
        drf_request = DRFRequest(request)
        return drf_request

# --- Authentication Views ---

class RegisterViewUnitTests(ViewTestBase):

    @patch('backend.views.RegisterSerializer') # Mock the serializer used by the view
    def test_register_success(self, MockRegisterSerializer):
        """Test successful registration POST request."""
        view = RegisterView.as_view()
        request_data = {
            'username': 'newuser', 'email': 'new@example.com',
            'password': 'password123', 'password2': 'password123'
        }
        request = self._create_drf_request('post', data=request_data)

        # Configure the mock serializer
        mock_serializer_instance = MockRegisterSerializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        # Mock the save method to return a dummy user object (or mock)
        mock_user = MagicMock(spec=User)
        mock_serializer_instance.save.return_value = mock_user
        # Mock the .data attribute for the response
        mock_serializer_instance.data = {'id': 1, 'username': 'newuser'} # Simplified response data

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        MockRegisterSerializer.assert_called_once_with(data=request_data)
        mock_serializer_instance.is_valid.assert_called_once_with()
        mock_serializer_instance.save.assert_called_once()
        # Check response data matches serializer's mocked .data
        # Note: RegisterView doesn't actually return the user data, it returns serializer.data
        # Let's adjust the test based on the actual view behavior (returns serializer data on create)
        # The RegisterSerializer itself returns the User instance from create(),
        # but the CreateAPIView returns serializer.data in the Response.
        # We need to mock serializer.data correctly.
        # Let's assume RegisterSerializer.data would return the created user info
        # For a CreateAPIView, the response data *is* serializer.data
        self.assertEqual(response.data, mock_serializer_instance.data)


    @patch('backend.views.RegisterSerializer')
    def test_register_invalid_data(self, MockRegisterSerializer):
        """Test registration POST request with invalid data."""
        view = RegisterView.as_view()
        request_data = {'username': 'bad'} # Incomplete data
        request = self._create_drf_request('post', data=request_data)

        # Configure the mock serializer for invalid data
        mock_serializer_instance = MockRegisterSerializer.return_value
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {'password': ['This field is required.']} # Example errors

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        MockRegisterSerializer.assert_called_once_with(data=request_data)
        mock_serializer_instance.is_valid.assert_called_once_with()
        mock_serializer_instance.save.assert_not_called() # Save should not be called
        self.assertEqual(response.data, mock_serializer_instance.errors)


class LoginViewUnitTests(ViewTestBase):

    @patch('backend.views.authenticate')
    @patch('backend.views.login')
    @patch('backend.views.UserSerializer')
    def test_login_success(self, MockUserSerializer, mock_login, mock_authenticate):
        """Test successful login POST request."""
        view = LoginView.as_view()
        request_data = {'username': 'testuser', 'password': 'password123'}
        request = self._create_drf_request('post', data=request_data)

        # Configure mocks
        mock_user = MagicMock(spec=User, username='testuser', id=1)
        mock_authenticate.return_value = mock_user
        mock_serializer_instance = MockUserSerializer.return_value
        mock_serializer_instance.data = {'id': 1, 'username': 'testuser', 'profile': {}} # Mocked response

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_authenticate.assert_called_once_with(request._request, username='testuser', password='password123')
        mock_login.assert_called_once_with(request._request, mock_user)
        MockUserSerializer.assert_called_once_with(mock_user, context={'request': request})
        self.assertEqual(response.data, mock_serializer_instance.data)

    @patch('backend.views.authenticate')
    @patch('backend.views.login')
    def test_login_invalid_credentials(self, mock_login, mock_authenticate):
        """Test login POST request with invalid credentials."""
        view = LoginView.as_view()
        request_data = {'username': 'testuser', 'password': 'wrongpassword'}
        request = self._create_drf_request('post', data=request_data)

        # Configure mocks
        mock_authenticate.return_value = None # Simulate failed authentication

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_authenticate.assert_called_once_with(request._request, username='testuser', password='wrongpassword')
        mock_login.assert_not_called() # Login should not be called
        self.assertEqual(response.data, {'error': 'Invalid credentials'})

    def test_login_missing_credentials(self):
        """Test login POST request with missing username or password."""
        view = LoginView.as_view()

        # Missing password
        request_no_pw = self._create_drf_request('post', data={'username': 'testuser'})
        response_no_pw = view(request_no_pw)
        self.assertEqual(response_no_pw.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_no_pw.data, {'error': 'Username and password are required'})

        # Missing username
        request_no_user = self._create_drf_request('post', data={'password': 'password123'})
        response_no_user = view(request_no_user)
        self.assertEqual(response_no_user.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_no_user.data, {'error': 'Username and password are required'})


class LogoutViewUnitTests(ViewTestBase):

    @patch('backend.views.logout')
    def test_logout_success(self, mock_logout):
        """Test successful logout POST request."""
        view = LogoutView.as_view()
        # Assume user is authenticated (permissions checked separately)
        request = self._create_drf_request('post', user=self.regular_user)

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_logout.assert_called_once_with(request._request)
        self.assertEqual(response.data, {"message": "Logged out successfully"})

# --- User Management Views ---

class UserListViewUnitTests(ViewTestBase):

    @patch('backend.views.UserSerializer')
    @patch.object(User.objects, 'select_related') # Mock the queryset method
    def test_list_users(self, mock_select_related, MockUserSerializer):
        """Test GET request to list users (logic assuming permission passed)."""
        # We don't test permissions here, just the view's queryset and serialization logic
        view = UserListView()
        request = self._create_drf_request('get', user=self.admin_user) # Assume admin

        # Configure mocks
        mock_queryset = MagicMock()
        mock_select_related.return_value.all.return_value = mock_queryset
        # Mock serializer behavior for a list
        MockUserSerializer.return_value.data = [{'id': 1, 'username': 'user1'}, {'id': 2, 'username': 'user2'}]

        # Simulate the steps ListAPIView takes (get_queryset, filter_queryset, paginate_queryset, get_serializer, data)
        # For unit testing, we can often simplify by checking the core parts
        queryset = view.get_queryset()
        serializer = view.get_serializer(queryset, many=True) # Simulate getting serializer for the queryset

        # Assertions
        mock_select_related.assert_called_once_with('profile')
        mock_select_related.return_value.all.assert_called_once()
        self.assertEqual(queryset, mock_queryset)
        # Check serializer was instantiated correctly (mocked instance check is tricky)
        MockUserSerializer.assert_called_with(queryset, many=True)
        # The actual response generation is complex in ListAPIView, focus on inputs/outputs
        # We can check that the serializer used is correct
        self.assertEqual(view.serializer_class, MockUserSerializer)


class CurrentUserViewUnitTests(ViewTestBase):

    @patch('backend.views.UserSerializer')
    def test_get_current_user(self, MockUserSerializer):
        """Test GET request for the current user."""
        view = CurrentUserView()
        request = self._create_drf_request('get', user=self.regular_user)
        view.request = request # Set request on the view instance

        # Configure mocks
        mock_serializer_instance = MockUserSerializer.return_value
        mock_serializer_instance.data = {'id': self.regular_user.id, 'username': self.regular_user.username}

        # Test get_object
        obj = view.get_object()
        self.assertEqual(obj, self.regular_user)

        # Test the response generation (simplified)
        serializer = view.get_serializer(obj)
        self.assertEqual(serializer.data, mock_serializer_instance.data)
        # The RetrieveAPIView handles the response creation, we tested the key parts


class CurrentUserUpdateViewUnitTests(ViewTestBase):

    @patch('backend.views.UserProfileSerializer')
    @patch('backend.views.UserSerializer')
    @patch('backend.views.update_session_auth_hash')
    def test_update_current_user_basic_info(self, mock_update_hash, MockUserSerializer, MockUserProfileSerializer):
        """Test PATCH request to update basic user info."""
        view = CurrentUserUpdateView()
        request_data = {'first_name': 'Updated', 'profile': {'age': 31}} # Include profile data
        request = self._create_drf_request('patch', user=self.regular_user, data=request_data)
        view.request = request
        view.format_kwarg = None # Needed for perform_update context

        # Mock the main UserSerializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        # Mock the save method to return the user and simulate updated data
        updated_user_mock = MagicMock(spec=User, id=self.regular_user.id, profile=self.regular_user.profile)
        mock_user_serializer_instance.save.return_value = updated_user_mock
        mock_user_serializer_instance.data = {'id': self.regular_user.id, 'first_name': 'Updated'} # Mock response data

        # Mock the UserProfileSerializer used internally
        mock_profile_serializer_instance = MockUserProfileSerializer.return_value
        mock_profile_serializer_instance.is_valid.return_value = True

        # Call perform_update directly (as RetrieveUpdateAPIView handles the main flow)
        view.perform_update(mock_user_serializer_instance)

        # Assertions
        # UserSerializer save should be called
        mock_user_serializer_instance.save.assert_called_once()
        # Profile serializer should be instantiated and validated/saved
        MockUserProfileSerializer.assert_called_once_with(
            updated_user_mock.profile, data={'age': 31}, partial=True, context={'request': request}
        )
        mock_profile_serializer_instance.is_valid.assert_called_once_with(raise_exception=True)
        mock_profile_serializer_instance.save.assert_called_once()
        # update_session_auth_hash should NOT be called if password wasn't updated
        mock_update_hash.assert_not_called()

    @patch('backend.views.UserProfileSerializer')
    @patch('backend.views.UserSerializer')
    @patch('backend.views.update_session_auth_hash')
    def test_update_current_user_password(self, mock_update_hash, MockUserSerializer, MockUserProfileSerializer):
        """Test PATCH request to update password."""
        view = CurrentUserUpdateView()
        request_data = {'password': 'newpassword123'}
        request = self._create_drf_request('patch', user=self.regular_user, data=request_data)
        view.request = request
        view.format_kwarg = None

        # Mock UserSerializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        updated_user_mock = MagicMock(spec=User, id=self.regular_user.id)
        # Mock the set_password and save methods on the user mock
        updated_user_mock.set_password = MagicMock()
        updated_user_mock.save = MagicMock()
        mock_user_serializer_instance.save.return_value = updated_user_mock

        # Call perform_update
        view.perform_update(mock_user_serializer_instance)

        # Assertions
        mock_user_serializer_instance.save.assert_called_once()
        updated_user_mock.set_password.assert_called_once_with('newpassword123')
        updated_user_mock.save.assert_called_once() # User saved after password set
        mock_update_hash.assert_called_once_with(request._request, updated_user_mock)
        # Profile serializer should not be called if 'profile' not in data
        MockUserProfileSerializer.assert_not_called()

    @patch('backend.views.UserProfileSerializer')
    @patch('backend.views.UserSerializer')
    def test_update_current_user_prevents_type_change(self, MockUserSerializer, MockUserProfileSerializer):
        """Test user cannot change their own type via profile update."""
        view = CurrentUserUpdateView()
        # Attempt to change type to Admin ('AD')
        request_data = {'profile': {'age': 32, 'type': 'AD'}}
        request = self._create_drf_request('patch', user=self.regular_user, data=request_data)
        view.request = request
        view.format_kwarg = None

        # Mock UserSerializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        updated_user_mock = MagicMock(spec=User, id=self.regular_user.id, profile=self.regular_user.profile)
        mock_user_serializer_instance.save.return_value = updated_user_mock

        # Mock ProfileSerializer
        mock_profile_serializer_instance = MockUserProfileSerializer.return_value
        mock_profile_serializer_instance.is_valid.return_value = True

        # Call perform_update
        view.perform_update(mock_user_serializer_instance)

        # Assertions
        # Check that UserProfileSerializer was called with 'type' removed from data
        expected_profile_data = {'age': 32} # 'type' should have been popped
        MockUserProfileSerializer.assert_called_once_with(
            updated_user_mock.profile, data=expected_profile_data, partial=True, context={'request': request}
        )
        mock_profile_serializer_instance.is_valid.assert_called_once_with(raise_exception=True)
        mock_profile_serializer_instance.save.assert_called_once()


# --- Book Management Views ---

class BookListCreateViewUnitTests(ViewTestBase):

    @patch('backend.views.BookSerializer')
    def test_perform_create_sets_added_by(self, MockBookSerializer):
        """Test perform_create sets added_by to the request user."""
        view = BookListCreateView()
        request = self._create_drf_request('post', user=self.librarian_user)
        view.request = request # Set request on view instance

        # Mock the serializer instance passed to perform_create
        mock_serializer_instance = MockBookSerializer.return_value

        # Call perform_create
        view.perform_create(mock_serializer_instance)

        # Assertions
        # Check that serializer.save() was called with added_by set
        mock_serializer_instance.save.assert_called_once_with(added_by=self.librarian_user)


class BorrowBookViewUnitTests(ViewTestBase):

    @patch('backend.views.BookSerializer')
    @patch('backend.views.get_object_or_404')
    @patch.object(Book.objects, 'filter') # Mock filter for borrow limit check
    def test_borrow_book_success(self, mock_filter, mock_get_object, MockBookSerializer):
        """Test successful book borrowing."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(id=1, available=True, borrower=None) # Use build for non-DB object
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_borrow
        # Mock borrow limit check - assume user is below limit
        mock_filter.return_value.count.return_value = 0
        # Mock the book's save method
        book_to_borrow.save = MagicMock()
        # Mock the serializer
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {'id': 1, 'title': 'Borrowed Book', 'available': False}

        response = view(request, book_id=book_to_borrow.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        # Check book attributes were set correctly before save
        self.assertFalse(book_to_borrow.available)
        self.assertEqual(book_to_borrow.borrower, self.regular_user)
        self.assertEqual(book_to_borrow.borrow_date, date.today())
        self.assertEqual(book_to_borrow.due_date, date.today() + timedelta(weeks=2))
        book_to_borrow.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_borrow, context={'request': request})
        self.assertEqual(response.data['message'], 'Book borrowed successfully')
        self.assertEqual(response.data['book'], mock_serializer_instance.data)

    @patch('backend.views.get_object_or_404')
    def test_borrow_book_unavailable(self, mock_get_object):
        """Test borrowing a book that is already unavailable."""
        view = BorrowBookView.as_view()
        other_user = UserFactory.build()
        book_unavailable = BookFactory.build(
            id=2, available=False, borrower=other_user, due_date=date.today() + timedelta(days=5)
        )
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_unavailable
        book_unavailable.save = MagicMock() # Should not be called

        response = view(request, book_id=book_unavailable.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_unavailable.id)
        self.assertIn('error', response.data)
        self.assertIn('unavailable', response.data['error'])
        book_unavailable.save.assert_not_called() # Save should not be called

    @patch('backend.views.get_object_or_404')
    @patch.object(Book.objects, 'filter')
    def test_borrow_book_limit_reached(self, mock_filter, mock_get_object):
        """Test borrowing when the user has reached the borrow limit."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(id=1, available=True, borrower=None)
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_borrow
        # Mock borrow limit check - assume user is AT the limit
        mock_filter.return_value.count.return_value = MAX_BORROW_LIMIT
        book_to_borrow.save = MagicMock() # Should not be called

        response = view(request, book_id=book_to_borrow.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        self.assertIn('error', response.data)
        self.assertIn('limit reached', response.data['error'].lower())
        book_to_borrow.save.assert_not_called()


class ReturnBookViewUnitTests(ViewTestBase):

    @patch('backend.views.BookSerializer')
    @patch('backend.views.get_object_or_404')
    def test_return_book_success_by_borrower(self, mock_get_object, MockBookSerializer):
        """Test successful return by the user who borrowed it."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(id=1, available=False, borrower=self.regular_user)
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_return
        book_to_return.save = MagicMock()
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {'id': 1, 'title': 'Returned Book', 'available': True}

        response = view(request, book_id=book_to_return.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_return.id)
        # Check book attributes were reset correctly before save
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)
        self.assertIsNone(book_to_return.borrow_date)
        self.assertIsNone(book_to_return.due_date)
        book_to_return.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_return, context={'request': request})
        self.assertEqual(response.data['message'], 'Book returned successfully')
        self.assertEqual(response.data['book'], mock_serializer_instance.data)

    @patch('backend.views.BookSerializer')
    @patch('backend.views.get_object_or_404')
    def test_return_book_success_by_admin(self, mock_get_object, MockBookSerializer):
        """Test successful return by an admin (even if borrowed by someone else)."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(id=1, available=False, borrower=self.regular_user)
        request = self._create_drf_request('post', user=self.admin_user) # Admin user

        # Configure mocks
        mock_get_object.return_value = book_to_return
        book_to_return.save = MagicMock()
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {'id': 1, 'title': 'Returned Book', 'available': True}

        response = view(request, book_id=book_to_return.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Admin can return
        book_to_return.save.assert_called_once()

    @patch('backend.views.get_object_or_404')
    def test_return_book_not_borrowed_by_user(self, mock_get_object):
        """Test returning a book not borrowed by the current (non-admin/librarian) user."""
        view = ReturnBookView.as_view()
        other_user = UserFactory.build()
        book_borrowed_by_other = BookFactory.build(id=1, available=False, borrower=other_user)
        # Use a different regular user to attempt return
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_borrowed_by_other
        book_borrowed_by_other.save = MagicMock()

        response = view(request, book_id=book_borrowed_by_other.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_get_object.assert_called_once_with(Book, id=book_borrowed_by_other.id)
        self.assertIn('error', response.data)
        self.assertIn('did not borrow', response.data['error'])
        book_borrowed_by_other.save.assert_not_called()

    @patch('backend.views.get_object_or_404')
    def test_return_book_already_available(self, mock_get_object):
        """Test returning a book that is already available."""
        view = ReturnBookView.as_view()
        book_available = BookFactory.build(id=1, available=True, borrower=None)
        request = self._create_drf_request('post', user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_available
        book_available.save = MagicMock()

        response = view(request, book_id=book_available.id)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_available.id)
        self.assertIn('error', response.data)
        self.assertIn('already available', response.data['error'])
        book_available.save.assert_not_called()


class BorrowedBooksListViewUnitTests(ViewTestBase):

    @patch('backend.views.BookSerializer')
    @patch.object(Book.objects, 'filter')
    def test_list_borrowed_for_regular_user(self, mock_filter, MockBookSerializer):
        """Test listing borrowed books for a regular user."""
        view = BorrowedBooksListView.as_view()
        request = self._create_drf_request('get', user=self.regular_user)

        # Configure mocks
        mock_book1 = BookFactory.build(id=1, title="Borrowed 1")
        mock_book2 = BookFactory.build(id=2, title="Borrowed 2")
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value.order_by.return_value = [mock_book1, mock_book2]
        mock_filter.return_value = mock_queryset
        # Mock serializer for multiple books
        MockBookSerializer.return_value.data = [
            {'id': 1, 'title': 'Borrowed 1'}, {'id': 2, 'title': 'Borrowed 2'}
        ]

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_queryset.select_related.assert_called_once_with('borrower', 'borrower__profile')
        mock_queryset.select_related.return_value.order_by.assert_called_once_with('due_date')
        MockBookSerializer.assert_called_with([mock_book1, mock_book2], many=True, context={'request': request})
        self.assertIn('my_borrowed_books', response.data)
        self.assertEqual(response.data['my_borrowed_books'], MockBookSerializer.return_value.data)

    @patch('backend.views.BookSerializer')
    @patch.object(Book.objects, 'filter')
    def test_list_borrowed_for_admin(self, mock_filter, MockBookSerializer):
        """Test listing all borrowed books for an admin."""
        view = BorrowedBooksListView.as_view()
        request = self._create_drf_request('get', user=self.admin_user)

        # Configure mocks
        user1 = UserFactory.build(id=10, username='borrower1')
        user2 = UserFactory.build(id=11, username='borrower2')
        mock_book1 = BookFactory.build(id=1, title="Book A", borrower=user1)
        mock_book2 = BookFactory.build(id=2, title="Book B", borrower=user2)
        mock_book3 = BookFactory.build(id=3, title="Book C", borrower=user1)
        mock_queryset = MagicMock()
        # Ensure select_related includes borrower profile for grouping logic
        mock_queryset.select_related.return_value.order_by.return_value = [mock_book1, mock_book3, mock_book2]
        mock_filter.return_value = mock_queryset

        # Mock the serializer to return data based on the input book
        def mock_serializer_side_effect(book, context=None, many=False):
            if many: # Should not be called with many=True in admin case
                 raise TypeError("Serializer called with many=True unexpectedly")
            # Return mock data based on book instance
            mock_data = {'id': book.id, 'title': book.title, 'borrower': book.borrower.username}
            mock_instance = MagicMock()
            mock_instance.data = mock_data
            return mock_instance

        MockBookSerializer.side_effect = mock_serializer_side_effect

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(available=False)
        mock_queryset.select_related.assert_called_once_with('borrower', 'borrower__profile')
        mock_queryset.select_related.return_value.order_by.assert_called_once_with('borrower__username', 'due_date')
        # Check serializer was called for each book
        self.assertEqual(MockBookSerializer.call_count, 3)
        MockBookSerializer.assert_any_call(mock_book1, context={'request': request})
        MockBookSerializer.assert_any_call(mock_book2, context={'request': request})
        MockBookSerializer.assert_any_call(mock_book3, context={'request': request})

        # Check response structure
        self.assertIn('borrowed_books_by_user', response.data)
        grouped_data = response.data['borrowed_books_by_user']
        self.assertEqual(len(grouped_data), 2) # Two borrowers

        # Check content (simplified)
        user1_data = next(g for g in grouped_data if g['borrower_name'] == 'borrower1')
        user2_data = next(g for g in grouped_data if g['borrower_name'] == 'borrower2')
        self.assertEqual(len(user1_data['books']), 2)
        self.assertEqual(len(user2_data['books']), 1)
        self.assertEqual(user1_data['books'][0]['title'], 'Book A')
        self.assertEqual(user1_data['books'][1]['title'], 'Book C')
        self.assertEqual(user2_data['books'][0]['title'], 'Book B')


# --- Utility Views ---

class CsrfTokenViewUnitTests(ViewTestBase):

    @patch('backend.views.get_token')
    def test_csrf_token_view(self, mock_get_token):
        """Test the csrf_token_view function."""
        request = self.factory.get('/api/csrf/') # Use raw factory request for function view
        mock_token_value = 'mockcsrftokenvalue12345'
        mock_get_token.return_value = mock_token_value

        response = csrf_token_view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_token.assert_called_once_with(request)
        # Response data is DRF Response, access .data
        self.assertEqual(response.data, {"csrfToken": mock_token_value})