# -*- coding: utf-8 -*-
"""
Unit tests for backend API views.
Focuses on testing view logic in isolation using mocks.
"""
import unittest
import json
from datetime import date, timedelta
from unittest.mock import (
    patch,
    MagicMock,
    ANY,
)

from django.test import TestCase # Keep TestCase
# <<< CHANGE: Import APIRequestFactory and force_authenticate >>>
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
# <<< CHANGE: Import HttpRequest >>>
from django.http import Http404, HttpRequest # Keep Http404 if needed, Add HttpRequest
# from django.urls import reverse # Keep if needed for URL lookups
from rest_framework import status
from rest_framework.request import Request as DRFRequest # Keep for type hints if needed
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
# Import DRF decorators for wrapping function view in test
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes


# Import views, models, serializers, permissions
from backend import views, models, serializers
from backend.models import UserProfile, Book
from backend.serializers import (
    UserSerializer,
    RegisterSerializer,
    BookSerializer,
    UserProfileSerializer,
)
from backend.views import (
    RegisterView, LoginView, LogoutView, UserListView, CurrentUserView,
    CurrentUserUpdateView, BookListCreateView, BorrowBookView, ReturnBookView,
    BorrowedBooksListView, csrf_token_view, MAX_BORROW_LIMIT
)


# Import factories
from ..factories import UserFactory, UserProfileFactory, BookFactory

User = get_user_model()

# --- Test Setup Helper ---


class ViewTestBase(TestCase):
    """Base class with APIRequestFactory and common setup."""

    def setUp(self):
        super().setUp()
        # <<< CHANGE: Use APIRequestFactory >>>
        self.factory = APIRequestFactory()
        self.anonymous_user = AnonymousUser()
        # Create users with profiles - these users ARE authenticated conceptually
        # but force_authenticate will handle the request object state
        self.regular_user = UserFactory(username="testuser_unit")
        UserProfileFactory(user=self.regular_user, type="US")
        self.librarian_user = UserFactory(username="testlibrarian_unit")
        UserProfileFactory(user=self.librarian_user, type="LB")
        self.admin_user = UserFactory(username="testadmin_unit")
        UserProfileFactory(user=self.admin_user, type="AD")

    # Removed _create_drf_request helper as APIRequestFactory is used directly


# --- Authentication Views ---


class RegisterViewUnitTests(ViewTestBase):
    # <<< CHANGE: Patch get_serializer method instead of the class >>>
    @patch.object(RegisterView, 'get_serializer')
    def test_register_success(self, mock_get_serializer):
        """Test successful registration POST request."""
        view = RegisterView.as_view()
        request_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "password2": "password123",
        }
        request = self.factory.post(
            "/fake-register/",
            data=request_data,
            format="json",
        )

        # <<< CHANGE: Configure mock serializer instance >>>
        mock_serializer_instance = MagicMock(spec=RegisterSerializer)
        mock_serializer_instance.is_valid.return_value = True
        mock_user = MagicMock(spec=User)
        mock_serializer_instance.save.return_value = mock_user
        mock_serializer_instance.data = {"id": 1, "username": "newuser"}
        # <<< CHANGE: Configure mock get_serializer to return the instance >>>
        mock_get_serializer.return_value = mock_serializer_instance

        response = view(request) # Pass the DRF request directly

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # Check status first
        # <<< CHANGE: Assert get_serializer was called >>>
        mock_get_serializer.assert_called_once_with(data=request_data)
        # <<< CHANGE: Assert methods on the returned mock instance >>>
        mock_serializer_instance.is_valid.assert_called_once_with(raise_exception=True)
        mock_serializer_instance.save.assert_called_once()
        self.assertEqual(response.data, mock_serializer_instance.data)


    # <<< CHANGE: Patch get_serializer method instead of the class >>>
    @patch.object(RegisterView, 'get_serializer')
    def test_register_invalid_data(self, mock_get_serializer):
        """Test registration POST request with invalid data."""
        view = RegisterView.as_view()
        request_data = {"username": "bad"}
        request = self.factory.post(
            "/fake-register/",
            data=request_data,
            format="json",
        )

        # <<< CHANGE: Configure mock serializer instance >>>
        mock_serializer_instance = MagicMock(spec=RegisterSerializer)
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {"password": ["This field is required."]}
        # Simulate ValidationError raised by is_valid(raise_exception=True)
        mock_serializer_instance.is_valid.side_effect = ValidationError(
            mock_serializer_instance.errors
        )
        # <<< CHANGE: Configure mock get_serializer to return the instance >>>
        mock_get_serializer.return_value = mock_serializer_instance

        response = view(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Check status first
        # <<< CHANGE: Assert get_serializer was called >>>
        mock_get_serializer.assert_called_once_with(data=request_data)
        # <<< CHANGE: Assert methods on the returned mock instance >>>
        mock_serializer_instance.is_valid.assert_called_once_with(raise_exception=True)
        mock_serializer_instance.save.assert_not_called()
        self.assertEqual(response.data, mock_serializer_instance.errors)


class LoginViewUnitTests(ViewTestBase):
    @patch("backend.views.authenticate")
    @patch("backend.views.login")
    @patch("backend.views.UserSerializer")
    def test_login_success(self, MockUserSerializer, mock_login, mock_authenticate):
        """Test successful login POST request."""
        view = LoginView.as_view()
        request_data = {"username": "testuser", "password": "password123"}
        request = self.factory.post(
            "/fake-login/",
            data=request_data,
            format="json",
        )

        mock_user = MagicMock(spec=User, username="testuser", id=1)
        mock_authenticate.return_value = mock_user
        mock_serializer_instance = MockUserSerializer.return_value
        mock_serializer_instance.data = {"id": 1, "username": "testuser", "profile": {}}

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # <<< CHANGE: Assert authenticate call arguments and type >>>
        mock_authenticate.assert_called_once()
        auth_call_args, auth_call_kwargs = mock_authenticate.call_args
        self.assertIsInstance(auth_call_args[0], HttpRequest) # Check type of first arg
        self.assertEqual(auth_call_kwargs['username'], "testuser")
        self.assertEqual(auth_call_kwargs['password'], "password123")

        # <<< CHANGE: Assert login call arguments and type >>>
        mock_login.assert_called_once()
        login_call_args, login_call_kwargs = mock_login.call_args
        self.assertIsInstance(login_call_args[0], HttpRequest) # Check type of first arg
        self.assertEqual(login_call_args[1], mock_user) # Check user object

        # Serializer context is handled automatically
        MockUserSerializer.assert_called_once_with(mock_user, context=ANY)
        self.assertEqual(response.data, mock_serializer_instance.data)

    @patch("backend.views.authenticate")
    @patch("backend.views.login")
    def test_login_invalid_credentials(self, mock_login, mock_authenticate):
        """Test login POST request with invalid credentials."""
        view = LoginView.as_view()
        request_data = {"username": "testuser", "password": "wrongpassword"}
        request = self.factory.post(
            "/fake-login/",
            data=request_data,
            format="json",
        )

        mock_authenticate.return_value = None

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # <<< CHANGE: Assert authenticate call arguments and type >>>
        mock_authenticate.assert_called_once()
        auth_call_args, auth_call_kwargs = mock_authenticate.call_args
        self.assertIsInstance(auth_call_args[0], HttpRequest) # Check type of first arg
        self.assertEqual(auth_call_kwargs['username'], "testuser")
        self.assertEqual(auth_call_kwargs['password'], "wrongpassword")

        mock_login.assert_not_called()
        self.assertEqual(response.data, {"error": "Invalid credentials"})

    def test_login_missing_credentials(self):
        """Test login POST request with missing username or password."""
        view = LoginView.as_view()

        request_no_pw = self.factory.post(
            "/fake-login/",
            data={"username": "testuser"},
            format="json",
        )
        response_no_pw = view(request_no_pw)
        self.assertEqual(response_no_pw.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_no_pw.data, {"error": "Username and password are required"})


        request_no_user = self.factory.post(
            "/fake-login/",
            data={"password": "password123"},
            format="json",
        )
        response_no_user = view(request_no_user)
        self.assertEqual(response_no_user.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_no_user.data, {"error": "Username and password are required"})


class LogoutViewUnitTests(ViewTestBase):
    @patch("backend.views.logout")
    def test_logout_success(self, mock_logout):
        """Test successful logout POST request."""
        view = LogoutView.as_view()
        request = self.factory.post("/fake-logout/")
        force_authenticate(request, user=self.regular_user)

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # <<< CHANGE: Assert logout call arguments and type >>>
        mock_logout.assert_called_once()
        logout_call_args, logout_call_kwargs = mock_logout.call_args
        self.assertIsInstance(logout_call_args[0], HttpRequest) # Check type of first arg

        self.assertEqual(response.data, {"message": "Logged out successfully"})


# --- User Management Views ---


class UserListViewUnitTests(ViewTestBase):
    # <<< CHANGE: Patch get_serializer method >>>
    @patch.object(UserListView, 'get_serializer')
    @patch.object(UserListView, "get_queryset")
    def test_list_users(self, mock_get_queryset, mock_get_serializer):
        """Test GET request to list users (logic assuming permission passed)."""
        view = UserListView.as_view()
        request = self.factory.get("/fake-users/")
        force_authenticate(request, user=self.admin_user)

        mock_user1 = MagicMock(spec=User)
        mock_user2 = MagicMock(spec=User)
        mock_queryset_result = [mock_user1, mock_user2]
        mock_get_queryset.return_value = mock_queryset_result

        # <<< CHANGE: Configure mock serializer instance >>>
        mock_serializer_instance = MagicMock(spec=UserSerializer)
        mock_serializer_instance.data = [{"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}]
        # <<< CHANGE: Configure mock get_serializer to return the instance >>>
        mock_get_serializer.return_value = mock_serializer_instance

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_queryset.assert_called_once()
        # <<< CHANGE: Assert get_serializer was called >>>
        # Note: get_serializer in ListAPIView is called with (queryset, many=True)
        mock_get_serializer.assert_called_once_with(mock_queryset_result, many=True)
        self.assertEqual(response.data, mock_serializer_instance.data)


class CurrentUserViewUnitTests(ViewTestBase):
    # <<< CHANGE: Patch get_serializer method >>>
    @patch.object(CurrentUserView, 'get_serializer')
    def test_get_current_user(self, mock_get_serializer):
        """Test GET request for the current user."""
        view_func = CurrentUserView.as_view()
        request = self.factory.get("/fake-me/")
        force_authenticate(request, user=self.regular_user)

        # <<< CHANGE: Configure mock serializer instance >>>
        mock_serializer_instance = MagicMock(spec=UserSerializer)
        mock_serializer_instance.data = {"id": self.regular_user.id, "username": self.regular_user.username}
        # <<< CHANGE: Configure mock get_serializer to return the instance >>>
        mock_get_serializer.return_value = mock_serializer_instance

        response = view_func(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # <<< CHANGE: Assert get_serializer was called >>>
        # Note: get_serializer in RetrieveAPIView is called with (instance)
        mock_get_serializer.assert_called_once_with(self.regular_user)
        self.assertEqual(response.data, mock_serializer_instance.data)




# --- Book Management Views ---


class BookListCreateViewUnitTests(ViewTestBase):
    # <<< CHANGE: Patch get_serializer method >>>
    @patch.object(BookListCreateView, 'get_serializer')
    def test_perform_create_sets_added_by(self, mock_get_serializer):
        """Test perform_create sets added_by to the request user."""
        view_func = BookListCreateView.as_view()
        request_data = {
            "title": "Test Book", "author": "Test", "isbn": "9999999999999",
            "category": "SF", "language": "Test", "condition": "GD",
        }
        request = self.factory.post(
            "/fake-books/",
            data=request_data,
            format="json",
        )
        force_authenticate(request, user=self.librarian_user)

        # <<< CHANGE: Configure mock serializer instance >>>
        mock_serializer_instance = MagicMock(spec=BookSerializer)
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = {"id": 99, **request_data}
        # <<< CHANGE: Configure mock get_serializer to return the instance >>>
        mock_get_serializer.return_value = mock_serializer_instance

        response = view_func(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # <<< CHANGE: Assert get_serializer was called >>>
        mock_get_serializer.assert_called_once_with(data=request_data)
        # <<< CHANGE: Assert methods on the returned mock instance >>>
        mock_serializer_instance.is_valid.assert_called_once_with(raise_exception=True)
        # Check save was called with added_by kwarg in perform_create
        mock_serializer_instance.save.assert_called_once_with(added_by=self.librarian_user)
        self.assertEqual(response.data, mock_serializer_instance.data)


class BorrowBookViewUnitTests(ViewTestBase):
    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    @patch.object(Book.objects, "filter")
    def test_borrow_book_success(self, mock_filter, mock_get_object, MockBookSerializer):
        """Test successful book borrowing."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(id=1, available=True, borrower=None) # Use build to avoid DB hit
        book_to_borrow.save = MagicMock() # Mock save method

        request = self.factory.post(f"/fake-borrow/{book_to_borrow.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_to_borrow
        # Simulate user has 0 books borrowed
        mock_filter.return_value.count.return_value = 0
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {"id": 1, "title": "Borrowed Book", "available": False}

        response = view(request, book_id=book_to_borrow.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        # Check borrow limit filter
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        # Check book state changes
        self.assertFalse(book_to_borrow.available)
        self.assertEqual(book_to_borrow.borrower, self.regular_user)
        self.assertEqual(book_to_borrow.borrow_date, date.today())
        self.assertEqual(book_to_borrow.due_date, date.today() + timedelta(weeks=2))
        book_to_borrow.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_borrow, context=ANY)
        self.assertEqual(response.data["message"], "Book borrowed successfully")
        self.assertEqual(response.data["book"], mock_serializer_instance.data)

    @patch("backend.views.get_object_or_404")
    def test_borrow_book_unavailable(self, mock_get_object):
        """Test borrowing a book that is already unavailable."""
        view = BorrowBookView.as_view()
        other_user = UserFactory.build(username="otherborrower")
        book_unavailable = BookFactory.build(
            id=2, available=False, borrower=other_user, due_date=date.today() + timedelta(days=5)
        )
        book_unavailable.save = MagicMock()

        request = self.factory.post(f"/fake-borrow/{book_unavailable.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_unavailable

        response = view(request, book_id=book_unavailable.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_unavailable.id)
        self.assertIn("error", response.data)
        self.assertIn("unavailable", response.data["error"])
        self.assertIn(other_user.username, response.data["error"])
        book_unavailable.save.assert_not_called()

    @patch("backend.views.get_object_or_404")
    @patch.object(Book.objects, "filter")
    def test_borrow_book_limit_reached(self, mock_filter, mock_get_object):
        """Test borrowing when the user has reached the borrow limit."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(id=1, available=True, borrower=None)
        book_to_borrow.save = MagicMock()

        request = self.factory.post(f"/fake-borrow/{book_to_borrow.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_to_borrow
        # Simulate user has reached borrow limit
        mock_filter.return_value.count.return_value = MAX_BORROW_LIMIT

        response = view(request, book_id=book_to_borrow.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        # Check borrow limit filter
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        self.assertIn("error", response.data)
        self.assertIn("limit reached", response.data["error"].lower())
        book_to_borrow.save.assert_not_called()


class ReturnBookViewUnitTests(ViewTestBase):
    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    def test_return_book_success_by_borrower(self, mock_get_object, MockBookSerializer):
        """Test successful return by the user who borrowed it."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(
            id=1, available=False, borrower=self.regular_user,
            borrow_date=date.today(), due_date=date.today() + timedelta(days=1)
        )
        book_to_return.save = MagicMock()

        request = self.factory.post(f"/fake-return/{book_to_return.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_to_return
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {"id": 1, "title": "Returned Book", "available": True}

        response = view(request, book_id=book_to_return.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_return.id)
        # Check book state changes
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)
        self.assertIsNone(book_to_return.borrow_date)
        self.assertIsNone(book_to_return.due_date)
        book_to_return.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_return, context=ANY)
        self.assertEqual(response.data["message"], "Book returned successfully")
        self.assertEqual(response.data["book"], mock_serializer_instance.data)

    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    def test_return_book_success_by_admin(self, mock_get_object, MockBookSerializer):
        """Test successful return by an admin (even if borrowed by someone else)."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(id=1, available=False, borrower=self.regular_user)
        book_to_return.save = MagicMock()

        request = self.factory.post(f"/fake-return/{book_to_return.id}/")
        force_authenticate(request, user=self.admin_user)

        mock_get_object.return_value = book_to_return
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {"id": 1, "title": "Returned Book", "available": True}

        response = view(request, book_id=book_to_return.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_return.id)
        book_to_return.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_return, context=ANY)

    @patch("backend.views.get_object_or_404")
    def test_return_book_not_borrowed_by_user(self, mock_get_object):
        """Test returning a book not borrowed by the current (non-admin/librarian) user."""
        view = ReturnBookView.as_view()
        other_user = UserFactory.build()
        book_borrowed_by_other = BookFactory.build(id=1, available=False, borrower=other_user)
        book_borrowed_by_other.save = MagicMock()

        request = self.factory.post(f"/fake-return/{book_borrowed_by_other.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_borrowed_by_other

        response = view(request, book_id=book_borrowed_by_other.id)

        # The permission check happens inside the view logic here
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_get_object.assert_called_once_with(Book, id=book_borrowed_by_other.id)
        self.assertIn("error", response.data)
        self.assertIn("did not borrow", response.data["error"])
        book_borrowed_by_other.save.assert_not_called()

    @patch("backend.views.get_object_or_404")
    def test_return_book_already_available(self, mock_get_object):
        """Test returning a book that is already available."""
        view = ReturnBookView.as_view()
        book_available = BookFactory.build(id=1, available=True, borrower=None)
        book_available.save = MagicMock()

        request = self.factory.post(f"/fake-return/{book_available.id}/")
        force_authenticate(request, user=self.regular_user)

        mock_get_object.return_value = book_available

        response = view(request, book_id=book_available.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_available.id)
        self.assertIn("error", response.data)
        self.assertIn("already available", response.data["error"])
        book_available.save.assert_not_called()


class BorrowedBooksListViewUnitTests(ViewTestBase):
    @patch("backend.views.BookSerializer")
    @patch.object(Book.objects, "filter")
    def test_list_borrowed_for_regular_user(self, mock_filter, MockBookSerializer):
        """Test listing borrowed books for a regular user."""
        view = BorrowedBooksListView.as_view()
        request = self.factory.get("/fake-borrowed/")
        force_authenticate(request, user=self.regular_user)

        mock_book1 = BookFactory.build(id=1, title="Borrowed 1")
        mock_book2 = BookFactory.build(id=2, title="Borrowed 2")
        # Mock the queryset chain
        mock_queryset = MagicMock()
        mock_select_related = MagicMock()
        mock_order_by = MagicMock()
        mock_queryset.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_order_by
        mock_order_by.__iter__.return_value = [mock_book1, mock_book2] # Make it iterable
        mock_filter.return_value = mock_queryset

        # <<< CHANGE: Configure mock serializer instance for many=True >>>
        mock_serializer_instance = MagicMock(spec=BookSerializer)
        mock_serializer_instance.data = [{"id": 1, "title": "Borrowed 1"}, {"id": 2, "title": "Borrowed 2"}]
        # Configure the mock serializer class to return the instance when called with many=True
        MockBookSerializer.configure_mock(return_value=mock_serializer_instance)


        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_queryset.select_related.assert_called_once_with('borrower', 'borrower__profile')
        mock_select_related.order_by.assert_called_once_with('due_date')
        # <<< CHANGE: Check serializer called correctly with many=True >>>
        MockBookSerializer.assert_called_once_with(mock_order_by, many=True, context=ANY)
        self.assertIn("my_borrowed_books", response.data)
        self.assertEqual(response.data["my_borrowed_books"], mock_serializer_instance.data)

    @patch("backend.views.BookSerializer")
    @patch.object(Book.objects, "filter")
    def test_list_borrowed_for_admin(self, mock_filter, MockBookSerializer):
        """Test listing all borrowed books for an admin."""
        view = BorrowedBooksListView.as_view()
        request = self.factory.get("/fake-borrowed/")
        force_authenticate(request, user=self.admin_user)

        # Use build to avoid DB hits, ensure profiles are attached
        user1 = UserFactory.build(id=10, username="borrower1")
        user2 = UserFactory.build(id=11, username="borrower2")
        user1.profile = UserProfileFactory.build(user=user1)
        user2.profile = UserProfileFactory.build(user=user2)
        mock_book1 = BookFactory.build(id=1, title="Book A", borrower=user1)
        mock_book2 = BookFactory.build(id=2, title="Book B", borrower=user2)
        mock_book3 = BookFactory.build(id=3, title="Book C", borrower=user1)

        # Mock queryset chain
        mock_queryset = MagicMock()
        mock_select_related = MagicMock()
        mock_order_by = MagicMock()
        mock_queryset.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_order_by
        # Make iterable for the loop in the view
        mock_order_by.__iter__.return_value = [mock_book1, mock_book3, mock_book2]
        mock_filter.return_value = mock_queryset

        # Mock the serializer side effect for individual book serialization
        def mock_serializer_side_effect(instance, context=None, many=False):
            # This side effect should only be called for individual books (many=False)
            if many:
                 raise TypeError("Serializer called with many=True unexpectedly in admin branch")
            self.assertIsNotNone(context)
            self.assertIn("request", context)
            mock_instance = MagicMock()
            # Simulate serializer output for a single book
            mock_data = { "id": instance.id, "title": instance.title, "borrower": instance.borrower.username }
            mock_instance.data = mock_data
            return mock_instance

        MockBookSerializer.side_effect = mock_serializer_side_effect

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(available=False)
        mock_queryset.select_related.assert_called_once_with('borrower', 'borrower__profile')
        mock_select_related.order_by.assert_called_once_with('borrower__username', 'due_date')
        # Check serializer called 3 times (once per book)
        self.assertEqual(MockBookSerializer.call_count, 3)
        MockBookSerializer.assert_any_call(mock_book1, context=ANY)
        MockBookSerializer.assert_any_call(mock_book2, context=ANY)
        MockBookSerializer.assert_any_call(mock_book3, context=ANY)

        # Check response structure
        self.assertIn("borrowed_books_by_user", response.data)
        grouped_data = response.data["borrowed_books_by_user"]
        self.assertEqual(len(grouped_data), 2) # Two borrowers
        user1_data = next(g for g in grouped_data if g["borrower_name"] == "borrower1")
        user2_data = next(g for g in grouped_data if g["borrower_name"] == "borrower2")
        self.assertEqual(len(user1_data["books"]), 2) # User1 has 2 books
        self.assertEqual(len(user2_data["books"]), 1) # User2 has 1 book
        # Check book data within groups (relies on side_effect mock data)
        self.assertEqual(user1_data["books"][0]["title"], "Book A")
        self.assertEqual(user1_data["books"][1]["title"], "Book C")
        self.assertEqual(user2_data["books"][0]["title"], "Book B")


