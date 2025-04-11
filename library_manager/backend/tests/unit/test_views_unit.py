# -*- coding: utf-8 -*-
"""
Unit tests for backend API views.
Focuses on testing view logic in isolation using mocks.
"""

import json
from datetime import date, timedelta
from unittest.mock import (
    patch,
    MagicMock,
    ANY,
)  # ANY is useful for asserting calls with dynamic args

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404, HttpRequest  # <<< Import HttpRequest
from django.urls import (
    reverse,
)  # Although not strictly used for requests, can be useful for context
from rest_framework import status
from rest_framework.request import Request as DRFRequest  # To wrap factory requests

# --- ADDED IMPORT ---
from rest_framework import permissions

# --- ADDED IMPORT ---
from rest_framework.exceptions import ValidationError


# Import views, models, serializers, permissions
from backend import views, models, serializers
from backend.views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserListView,
    CurrentUserView,
    UserDetailView,
    CurrentUserUpdateView,
    BookListCreateView,
    BookDetailView,
    BorrowBookView,
    ReturnBookView,
    BorrowedBooksListView,
    csrf_token_view,
    MAX_BORROW_LIMIT,
)
from backend.models import UserProfile, Book
from backend.serializers import (
    UserSerializer,
    RegisterSerializer,
    BookSerializer,
    UserProfileSerializer,
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
        self.regular_user = UserFactory(username="testuser_unit")
        UserProfileFactory(user=self.regular_user, type="US")
        self.librarian_user = UserFactory(username="testlibrarian_unit")
        UserProfileFactory(user=self.librarian_user, type="LB")
        self.admin_user = UserFactory(username="testadmin_unit")
        UserProfileFactory(user=self.admin_user, type="AD")

    def _create_drf_request(
        self, method="get", path="/fake-path/", user=None, data=None, format="json"
    ):
        """Creates a DRF Request object wrapped around a RequestFactory request."""
        user = user or self.anonymous_user
        factory_method = getattr(self.factory, method)
        # For POST/PUT/PATCH etc., pass data; for GET, pass data as query params
        if method.lower() in ["post", "put", "patch", "delete"]:
            # Ensure data is serialized if it's a dict and format is json
            content_type = f"application/{format}"
            if isinstance(data, dict) and format == "json":
                data = json.dumps(data)
            else:
                # Handle form data etc. if needed, otherwise pass as is
                content_type = (
                    "application/x-www-form-urlencoded"  # Or multipart/form-data
                )

            request = factory_method(path, data=data, content_type=content_type)
        else:
            request = factory_method(path, data=data)  # GET data becomes query params

        request.user = user
        # Wrap with DRF Request
        drf_request = DRFRequest(request)
        # Also attach the original user to the DRF request explicitly if needed, though it should proxy
        # drf_request.user = user
        return drf_request


# --- Authentication Views ---


class RegisterViewUnitTests(ViewTestBase):
    @patch("backend.views.RegisterSerializer")  # Mock the serializer used by the view
    def test_register_success(self, MockRegisterSerializer):
        """Test successful registration POST request."""
        view = RegisterView.as_view()
        request_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "password2": "password123",
        }
        request = self._create_drf_request("post", data=request_data)

        # Configure the mock serializer
        mock_serializer_instance = MockRegisterSerializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        # Mock the save method to return a dummy user object (or mock)
        mock_user = MagicMock(spec=User)
        mock_serializer_instance.save.return_value = mock_user
        # Mock the .data attribute for the response
        mock_serializer_instance.data = {
            "id": 1,
            "username": "newuser",
        }  # Simplified response data

        # --- FIX: Pass DRF request to the view ---
        response = view(request)  # Pass the DRF Request

        # Assertions
        # --- EXPECTING 201 CREATED ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # --- FIX: Pass request.data when checking serializer call ---
        # DRF extracts data from request._request internally
        # --- EXPECTING CALL ---
        # The view will create a new DRF request internally, so we check the data passed
        MockRegisterSerializer.assert_called_once_with(
            data=request.data, context=ANY
        )  # Check context too
        mock_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )  # CreateAPIView calls with raise_exception=True
        mock_serializer_instance.save.assert_called_once()
        # Check response data matches serializer's mocked .data
        # For a CreateAPIView, the response data *is* serializer.data
        self.assertEqual(
            response.data, mock_serializer_instance.data
        )  # Check response data

    @patch("backend.views.RegisterSerializer")
    def test_register_invalid_data(self, MockRegisterSerializer):
        """Test registration POST request with invalid data."""
        view = RegisterView.as_view()
        request_data = {"username": "bad"}  # Incomplete data
        # --- Store the original data dictionary ---
        original_request_data = request_data.copy()
        request = self._create_drf_request("post", data=request_data)

        # Configure the mock serializer for invalid data
        mock_serializer_instance = MockRegisterSerializer.return_value
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {
            "password": ["This field is required."]
        }  # Example errors
        # --- Simulate the Validation Error raised by is_valid(raise_exception=True) ---
        mock_serializer_instance.is_valid.side_effect = ValidationError(
            mock_serializer_instance.errors
        )

        # --- FIX: Pass DRF request to the view ---
        response = view(request)  # Pass the DRF Request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # --- FIX: Assert serializer was called with the original data dict ---
        # --- EXPECTING CALL ---
        MockRegisterSerializer.assert_called_once_with(
            data=original_request_data, context=ANY
        )  # Check context too
        mock_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )  # CreateAPIView calls with raise_exception=True
        mock_serializer_instance.save.assert_not_called()  # Save should not be called
        self.assertEqual(response.data, mock_serializer_instance.errors)


class LoginViewUnitTests(ViewTestBase):
    @patch("backend.views.authenticate")
    @patch("backend.views.login")
    @patch("backend.views.UserSerializer")
    def test_login_success(
        self, MockUserSerializer, mock_login, mock_authenticate
    ):  # No permission patch here
        """Test successful login POST request."""
        view = LoginView.as_view()
        request_data = {"username": "testuser", "password": "password123"}
        request = self._create_drf_request("post", data=request_data)

        # Configure mocks
        mock_user = MagicMock(spec=User, username="testuser", id=1)
        mock_authenticate.return_value = mock_user
        mock_serializer_instance = MockUserSerializer.return_value
        mock_serializer_instance.data = {
            "id": 1,
            "username": "testuser",
            "profile": {},
        }  # Mocked response

        # --- FIX: Pass DRF request to the view ---
        response = view(request)  # Pass the DRF Request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # --- FIX: Assert authenticate called with DRF request ---
        mock_authenticate.assert_called_once_with(
            request, username="testuser", password="password123"
        )
        # --- Assert login called with underlying HttpRequest ---
        mock_login.assert_called_once_with(request._request, mock_user)
        # --- FIX: Serializer context should contain the DRF request ---
        # The view internally creates a DRF request, so we check context contains ANY DRF request
        MockUserSerializer.assert_called_once_with(mock_user, context=ANY)
        # Check that the context passed contains a DRF request object
        context_arg = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)
        self.assertEqual(response.data, mock_serializer_instance.data)

    @patch("backend.views.authenticate")
    @patch("backend.views.login")
    def test_login_invalid_credentials(self, mock_login, mock_authenticate):
        """Test login POST request with invalid credentials."""
        view = LoginView.as_view()
        request_data = {"username": "testuser", "password": "wrongpassword"}
        request = self._create_drf_request("post", data=request_data)

        # Configure mocks
        mock_authenticate.return_value = None  # Simulate failed authentication

        # --- FIX: Pass DRF request to the view ---
        response = view(request)  # Pass the DRF Request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # --- FIX: Assert authenticate called with DRF request ---
        mock_authenticate.assert_called_once_with(
            request, username="testuser", password="wrongpassword"
        )
        mock_login.assert_not_called()  # Login should not be called
        self.assertEqual(response.data, {"error": "Invalid credentials"})

    def test_login_missing_credentials(self):
        """Test login POST request with missing username or password."""
        view = LoginView.as_view()

        # Missing password
        request_no_pw = self._create_drf_request("post", data={"username": "testuser"})
        # --- FIX: Pass DRF request to the view ---
        response_no_pw = view(request_no_pw)  # Pass the DRF Request
        self.assertEqual(response_no_pw.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_no_pw.data, {"error": "Username and password are required"}
        )

        # Missing username
        request_no_user = self._create_drf_request(
            "post", data={"password": "password123"}
        )
        # --- FIX: Pass DRF request to the view ---
        response_no_user = view(request_no_user)  # Pass the DRF Request
        self.assertEqual(response_no_user.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_no_user.data, {"error": "Username and password are required"}
        )


class LogoutViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.LogoutView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.logout")
    def test_logout_success(
        self, mock_logout, mock_perms
    ):  # mock_perms is from outermost patch
        """Test successful logout POST request."""
        view = LogoutView.as_view()
        # Assume user is authenticated (permissions checked separately)
        request = self._create_drf_request("post", user=self.regular_user)

        # --- FIX: Pass DRF request to the view ---
        response = view(request)  # Pass the DRF Request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # --- Assert logout called with underlying HttpRequest ---
        mock_logout.assert_called_once_with(request._request)
        self.assertEqual(response.data, {"message": "Logged out successfully"})


# --- User Management Views ---


class UserListViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.UserListView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.UserSerializer")
    @patch.object(UserListView, "get_queryset")
    def test_list_users(
        self, mock_get_queryset, MockUserSerializer, mock_perms
    ):  # Innermost first
        """Test GET request to list users (logic assuming permission passed)."""
        # We don't test permissions here, just the view's queryset and serialization logic
        view = UserListView.as_view()
        request = self._create_drf_request(
            "get", path="/fake-users/", user=self.admin_user
        )  # Assume admin

        # Configure mocks
        # Mock the queryset returned by get_queryset
        mock_user1 = MagicMock(spec=User)
        mock_user2 = MagicMock(spec=User)
        mock_queryset_result = [mock_user1, mock_user2]
        mock_get_queryset.return_value = mock_queryset_result

        # Mock the serializer *instance* data that the view will use when it calls the serializer
        # --- FIX: Mock the data attribute of the serializer instance ---
        mock_serializer_instance = MagicMock()  # Create a mock instance
        mock_serializer_instance.data = [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"},
        ]
        # Configure the Serializer Class mock to return this instance
        MockUserSerializer.return_value = mock_serializer_instance

        # Call the view using the DRF Request
        response = view(request)  # Pass the DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_queryset.assert_called_once()  # Check that our mocked queryset method was called by the view

        # Check that the serializer class was instantiated correctly by the view
        # The view calls get_serializer(queryset, many=True) internally
        # --- FIX: Check context contains a DRF request ---
        MockUserSerializer.assert_called_with(
            mock_queryset_result, many=True, context=ANY
        )  # Check instantiation args
        context_arg = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)

        # Check that the response data matches the mocked serializer data
        self.assertEqual(response.data, mock_serializer_instance.data)

        # --- Optional: Check original queryset logic separately if needed ---
        # This verifies the underlying query logic if you haven't mocked get_queryset
        # with patch.object(User.objects, 'select_related') as mock_select_related:
        #     original_view_instance = UserListView() # Create separate instance just for this check
        #     # You might need to manually set request if methods depend on it directly
        #     # original_view_instance.request = request
        #     original_view_instance.get_queryset() # Call original method
        #     mock_select_related.assert_called_once_with('profile')
        #     mock_select_related.return_value.all.assert_called_once()


class CurrentUserViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.CurrentUserView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.UserSerializer")
    def test_get_current_user(self, MockUserSerializer, mock_perms):  # Innermost first
        """Test GET request for the current user."""
        # --- FIX: Use as_view() ---
        view_func = CurrentUserView.as_view()
        request = self._create_drf_request("get", user=self.regular_user)
        # --- FIX: Don't set request on view instance manually ---
        # view.request = request # Set request on the view instance

        # Configure mocks
        mock_serializer_instance = MockUserSerializer.return_value
        mock_serializer_instance.data = {
            "id": self.regular_user.id,
            "username": self.regular_user.username,
        }

        # --- FIX: Call the view function with DRF request ---
        response = view_func(request)  # Pass the DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check serializer was called with the correct user
        # The view internally calls get_object() which returns request.user
        MockUserSerializer.assert_called_once_with(self.regular_user, context=ANY)
        context_arg = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)
        self.assertEqual(response.data, mock_serializer_instance.data)

        # --- Test get_object separately if needed, but calling the view is better ---
        # view_instance = CurrentUserView()
        # view_instance.request = request # Need DRF request here for get_object
        # obj = view_instance.get_object()
        # self.assertEqual(obj, self.regular_user)


class CurrentUserUpdateViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.CurrentUserUpdateView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.UserProfileSerializer")
    @patch("backend.views.UserSerializer")
    @patch("backend.views.update_session_auth_hash")
    def test_update_current_user_basic_info(
        self,
        mock_update_hash,
        MockUserSerializer,
        MockUserProfileSerializer,
        mock_perms,
    ):  # Innermost first
        """Test PATCH request to update basic user info."""
        # --- Use as_view() to get the callable view ---
        view = CurrentUserUpdateView.as_view()
        request_data = {
            "first_name": "Updated",
            "profile": {"age": 31},
        }  # Include profile data
        # --- Create the request using the helper ---
        # Note: No pk needed in URL for CurrentUserUpdateView
        request = self._create_drf_request(
            "patch",
            path="/fake-update/",
            user=self.regular_user,
            data=request_data,
            format="json",
        )

        # --- Mock the main UserSerializer ---
        # Mock the instance returned by get_serializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        # Mock the save method to return the user and simulate updated data
        # The view will fetch this user via get_object()
        user_instance = self.regular_user
        mock_user_serializer_instance.save.return_value = user_instance
        mock_user_serializer_instance.data = {
            "id": user_instance.id,
            "first_name": "Updated",
        }  # Mock response data

        # --- Mock the UserProfileSerializer used internally ---
        mock_profile_serializer_instance = MockUserProfileSerializer.return_value
        mock_profile_serializer_instance.is_valid.return_value = True

        # --- Call the view directly using the DRF request ---
        response = view(request)  # Pass the DRF request

        # --- Assertions ---
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )  # Check for successful update status
        # Check UserSerializer was instantiated correctly by the view
        # The view calls get_object() -> self.regular_user
        # Then get_serializer(instance=user, data=request.data, partial=True)
        # We need to check the call to the Serializer class, not the instance
        # --- FIX: Check context contains DRF request ---
        MockUserSerializer.assert_called_with(
            instance=user_instance, data=request.data, partial=True, context=ANY
        )  # Check instantiation
        context_arg_user = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg_user)
        self.assertIsInstance(context_arg_user["request"], DRFRequest)

        mock_user_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_user_serializer_instance.save.assert_called_once()

        # Profile serializer should be instantiated and validated/saved within perform_update
        # Note: perform_update is called internally by the view's update method
        # --- FIX: Check context contains DRF request ---
        MockUserProfileSerializer.assert_called_once_with(
            user_instance.profile,
            data={"age": 31},
            partial=True,
            context=ANY,  # Context will be passed by view
        )
        context_arg_profile = MockUserProfileSerializer.call_args.kwargs.get(
            "context", {}
        )
        self.assertIn("request", context_arg_profile)
        self.assertIsInstance(context_arg_profile["request"], DRFRequest)

        mock_profile_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_profile_serializer_instance.save.assert_called_once()
        # update_session_auth_hash should NOT be called if password wasn't updated
        mock_update_hash.assert_not_called()
        # Check response data
        self.assertEqual(response.data, mock_user_serializer_instance.data)

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.CurrentUserUpdateView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.UserProfileSerializer")
    @patch("backend.views.UserSerializer")
    @patch("backend.views.update_session_auth_hash")
    def test_update_current_user_password(
        self,
        mock_update_hash,
        MockUserSerializer,
        MockUserProfileSerializer,
        mock_perms,
    ):  # Innermost first
        """Test PATCH request to update password."""
        view = CurrentUserUpdateView.as_view()
        request_data = {"password": "newpassword123"}
        request = self._create_drf_request(
            "patch",
            path="/fake-update/",
            user=self.regular_user,
            data=request_data,
            format="json",
        )

        # Mock UserSerializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        user_instance = self.regular_user
        # Mock the set_password and save methods on the actual user instance
        user_instance.set_password = MagicMock()
        user_instance.save = MagicMock()  # Mock save on the user model instance
        mock_user_serializer_instance.save.return_value = (
            user_instance  # Serializer.save still returns the instance
        )
        mock_user_serializer_instance.data = {
            "id": user_instance.id,
            "username": user_instance.username,
        }  # Mock response

        # Call the view with DRF request
        response = view(request)  # Pass the DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MockUserSerializer.assert_called_with(
            instance=user_instance, data=request.data, partial=True, context=ANY
        )
        context_arg = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)

        mock_user_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_user_serializer_instance.save.assert_called_once()  # Serializer save is called first
        # Check methods called within perform_update
        user_instance.set_password.assert_called_once_with("newpassword123")
        user_instance.save.assert_called_once()  # User saved after password set
        # --- Assert update_session_auth_hash called with underlying HttpRequest ---
        mock_update_hash.assert_called_once_with(
            request._request, user_instance
        )  # Pass the underlying HttpRequest
        # Profile serializer should not be called if 'profile' not in data
        MockUserProfileSerializer.assert_not_called()

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.CurrentUserUpdateView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.UserProfileSerializer")
    @patch("backend.views.UserSerializer")
    @patch(
        "backend.views.update_session_auth_hash"
    )  # Still need to patch this even if not called
    def test_update_current_user_prevents_type_change(
        self,
        mock_update_hash,
        MockUserSerializer,
        MockUserProfileSerializer,
        mock_perms,
    ):  # Innermost first
        """Test user cannot change their own type via profile update."""
        view = CurrentUserUpdateView.as_view()
        # Attempt to change type to Admin ('AD')
        request_data = {"profile": {"age": 32, "type": "AD"}}
        request = self._create_drf_request(
            "patch",
            path="/fake-update/",
            user=self.regular_user,
            data=request_data,
            format="json",
        )

        # Mock UserSerializer
        mock_user_serializer_instance = MockUserSerializer.return_value
        mock_user_serializer_instance.is_valid.return_value = True
        user_instance = self.regular_user
        mock_user_serializer_instance.save.return_value = user_instance
        mock_user_serializer_instance.data = {
            "id": user_instance.id,
            "username": user_instance.username,
        }  # Mock response

        # Mock ProfileSerializer
        mock_profile_serializer_instance = MockUserProfileSerializer.return_value
        mock_profile_serializer_instance.is_valid.return_value = True

        # Call the view with DRF request
        response = view(request)  # Pass the DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MockUserSerializer.assert_called_with(
            instance=user_instance, data=request.data, partial=True, context=ANY
        )
        context_arg_user = MockUserSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg_user)
        self.assertIsInstance(context_arg_user["request"], DRFRequest)

        mock_user_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_user_serializer_instance.save.assert_called_once()

        # Check that UserProfileSerializer was called with 'type' removed from data within perform_update
        expected_profile_data = {"age": 32}  # 'type' should have been popped
        MockUserProfileSerializer.assert_called_once_with(
            user_instance.profile, data=expected_profile_data, partial=True, context=ANY
        )
        context_arg_profile = MockUserProfileSerializer.call_args.kwargs.get(
            "context", {}
        )
        self.assertIn("request", context_arg_profile)
        self.assertIsInstance(context_arg_profile["request"], DRFRequest)

        mock_profile_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_profile_serializer_instance.save.assert_called_once()
        mock_update_hash.assert_not_called()  # Password not changed


# --- Book Management Views ---


class BookListCreateViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BookListCreateView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    def test_perform_create_sets_added_by(
        self, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test perform_create sets added_by to the request user."""
        # Use as_view() to get the callable view function
        view_func = BookListCreateView.as_view()
        # Create a request with the librarian user and some minimal valid data
        request_data = {
            "title": "Test Book",
            "author": "Test",
            "isbn": "9999999999999",
            "category": "SF",
            "language": "Test",
            "condition": "GD",
        }
        request = self._create_drf_request(
            "post", user=self.librarian_user, data=request_data, format="json"
        )

        # Mock the serializer instance that the view will create and use
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        # Mock the .data attribute for the response after creation
        mock_serializer_instance.data = {
            "id": 99,
            **request_data,
        }  # Simulate response data

        # Call the view function with the DRF Request
        response = view_func(request)  # Pass the DRF request

        # Assertions
        # Check the response status code indicates successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the serializer was instantiated with the request data
        MockBookSerializer.assert_called_with(data=request.data, context=ANY)
        # Check that is_valid was called
        mock_serializer_instance.is_valid.assert_called_once_with(
            raise_exception=True
        )  # ListCreateAPIView calls with raise_exception=True
        # Check that serializer.save() was called with added_by set correctly
        # This happens inside perform_create, which is called by the view's create method
        mock_serializer_instance.save.assert_called_once_with(
            added_by=self.librarian_user
        )
        # Check the response data matches the mocked serializer data
        self.assertEqual(response.data, mock_serializer_instance.data)


class BorrowBookViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BorrowBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    @patch.object(Book.objects, "filter")  # Mock filter for borrow limit check
    def test_borrow_book_success(
        self, mock_filter, mock_get_object, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test successful book borrowing."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(
            id=1, available=True, borrower=None
        )  # Use build for non-DB object
        # --- Use the regular user who should be allowed to borrow ---
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_borrow
        mock_filter.return_value.count.return_value = 0
        book_to_borrow.save = MagicMock()
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {
            "id": 1,
            "title": "Borrowed Book",
            "available": False,
        }

        # --- Call view with DRF request ---
        response = view(request, book_id=book_to_borrow.id)  # Pass DRF request

        # Assertions (Keep existing assertions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        self.assertFalse(book_to_borrow.available)
        self.assertEqual(book_to_borrow.borrower, self.regular_user)
        self.assertEqual(book_to_borrow.borrow_date, date.today())
        self.assertEqual(book_to_borrow.due_date, date.today() + timedelta(weeks=2))
        book_to_borrow.save.assert_called_once()
        MockBookSerializer.assert_called_once_with(book_to_borrow, context=ANY)
        context_arg = MockBookSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)
        self.assertEqual(response.data["message"], "Book borrowed successfully")
        self.assertEqual(response.data["book"], mock_serializer_instance.data)

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BorrowBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.get_object_or_404")
    def test_borrow_book_unavailable(
        self, mock_get_object, mock_perms
    ):  # Innermost first
        """Test borrowing a book that is already unavailable."""
        view = BorrowBookView.as_view()
        other_user = UserFactory.build(username="otherborrower")
        book_unavailable = BookFactory.build(
            id=2,
            available=False,
            borrower=other_user,
            due_date=date.today() + timedelta(days=5),
        )
        # --- Use the regular user ---
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_unavailable
        book_unavailable.save = MagicMock()  # Should not be called

        # --- Call view with DRF request ---
        response = view(request, book_id=book_unavailable.id)  # Pass DRF request

        # Assertions (Keep existing assertions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_unavailable.id)
        self.assertIn("error", response.data)
        self.assertIn("unavailable", response.data["error"])
        self.assertIn(other_user.username, response.data["error"])
        book_unavailable.save.assert_not_called()

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BorrowBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.get_object_or_404")
    @patch.object(Book.objects, "filter")
    def test_borrow_book_limit_reached(
        self, mock_filter, mock_get_object, mock_perms
    ):  # Innermost first
        """Test borrowing when the user has reached the borrow limit."""
        view = BorrowBookView.as_view()
        book_to_borrow = BookFactory.build(id=1, available=True, borrower=None)
        # --- Use the regular user ---
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_borrow
        mock_filter.return_value.count.return_value = MAX_BORROW_LIMIT
        book_to_borrow.save = MagicMock()  # Should not be called

        # --- Call view with DRF request ---
        response = view(request, book_id=book_to_borrow.id)  # Pass DRF request

        # Assertions (Keep existing assertions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_to_borrow.id)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_filter.return_value.count.assert_called_once()
        self.assertIn("error", response.data)
        self.assertIn("limit reached", response.data["error"].lower())
        book_to_borrow.save.assert_not_called()


class ReturnBookViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.ReturnBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    def test_return_book_success_by_borrower(
        self, mock_get_object, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test successful return by the user who borrowed it."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(
            id=1,
            available=False,
            borrower=self.regular_user,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=1),
        )
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_to_return
        book_to_return.save = MagicMock()
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {
            "id": 1,
            "title": "Returned Book",
            "available": True,
        }

        # --- Call view with DRF request ---
        response = view(request, book_id=book_to_return.id)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_object.assert_called_once_with(Book, id=book_to_return.id)
        # Check book attributes were reset correctly before save
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)
        self.assertIsNone(book_to_return.borrow_date)
        self.assertIsNone(book_to_return.due_date)
        book_to_return.save.assert_called_once()
        # --- FIX: Check context contains DRF request ---
        MockBookSerializer.assert_called_once_with(book_to_return, context=ANY)
        context_arg = MockBookSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)

        self.assertEqual(response.data["message"], "Book returned successfully")
        self.assertEqual(response.data["book"], mock_serializer_instance.data)

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.ReturnBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    @patch("backend.views.get_object_or_404")
    def test_return_book_success_by_admin(
        self, mock_get_object, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test successful return by an admin (even if borrowed by someone else)."""
        view = ReturnBookView.as_view()
        book_to_return = BookFactory.build(
            id=1, available=False, borrower=self.regular_user
        )
        request = self._create_drf_request("post", user=self.admin_user)  # Admin user

        # Configure mocks
        mock_get_object.return_value = book_to_return
        book_to_return.save = MagicMock()
        mock_serializer_instance = MockBookSerializer.return_value
        mock_serializer_instance.data = {
            "id": 1,
            "title": "Returned Book",
            "available": True,
        }

        # --- Call view with DRF request ---
        response = view(request, book_id=book_to_return.id)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Admin can return
        book_to_return.save.assert_called_once()

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.ReturnBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.get_object_or_404")
    def test_return_book_not_borrowed_by_user(
        self, mock_get_object, mock_perms
    ):  # Innermost first
        """Test returning a book not borrowed by the current (non-admin/librarian) user."""
        view = ReturnBookView.as_view()
        other_user = UserFactory.build()
        book_borrowed_by_other = BookFactory.build(
            id=1, available=False, borrower=other_user
        )
        # Use a different regular user to attempt return
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_borrowed_by_other
        book_borrowed_by_other.save = MagicMock()

        # --- Call view with DRF request ---
        response = view(request, book_id=book_borrowed_by_other.id)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_get_object.assert_called_once_with(Book, id=book_borrowed_by_other.id)
        self.assertIn("error", response.data)
        self.assertIn("did not borrow", response.data["error"])
        book_borrowed_by_other.save.assert_not_called()

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.ReturnBookView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.get_object_or_404")
    def test_return_book_already_available(
        self, mock_get_object, mock_perms
    ):  # Innermost first
        """Test returning a book that is already available."""
        view = ReturnBookView.as_view()
        book_available = BookFactory.build(id=1, available=True, borrower=None)
        request = self._create_drf_request("post", user=self.regular_user)

        # Configure mocks
        mock_get_object.return_value = book_available
        book_available.save = MagicMock()

        # --- Call view with DRF request ---
        response = view(request, book_id=book_available.id)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get_object.assert_called_once_with(Book, id=book_available.id)
        self.assertIn("error", response.data)
        self.assertIn("already available", response.data["error"])
        book_available.save.assert_not_called()


class BorrowedBooksListViewUnitTests(ViewTestBase):
    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BorrowedBooksListView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    @patch.object(Book.objects, "filter")
    def test_list_borrowed_for_regular_user(
        self, mock_filter, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test listing borrowed books for a regular user."""
        view = BorrowedBooksListView.as_view()
        request = self._create_drf_request("get", user=self.regular_user)

        # Configure mocks
        mock_book1 = BookFactory.build(id=1, title="Borrowed 1")
        mock_book2 = BookFactory.build(id=2, title="Borrowed 2")
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value.order_by.return_value = [
            mock_book1,
            mock_book2,
        ]
        mock_filter.return_value = mock_queryset
        # Mock serializer for multiple books
        # --- FIX: Mock the data attribute of the serializer instance ---
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = [
            {"id": 1, "title": "Borrowed 1"},
            {"id": 2, "title": "Borrowed 2"},
        ]
        MockBookSerializer.return_value = mock_serializer_instance

        # --- Call view with DRF request ---
        response = view(request)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(borrower=self.regular_user, available=False)
        mock_queryset.select_related.assert_called_once_with(
            "borrower", "borrower__profile"
        )
        mock_queryset.select_related.return_value.order_by.assert_called_once_with(
            "due_date"
        )
        # --- FIX: Check context contains DRF request ---
        MockBookSerializer.assert_called_with(
            [mock_book1, mock_book2], many=True, context=ANY
        )
        context_arg = MockBookSerializer.call_args.kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)

        self.assertIn("my_borrowed_books", response.data)
        self.assertEqual(
            response.data["my_borrowed_books"], mock_serializer_instance.data
        )

    # --- FIX: Correct argument order ---
    @patch(
        "backend.views.BorrowedBooksListView.permission_classes", [permissions.AllowAny]
    )  # Bypass permissions
    @patch("backend.views.BookSerializer")
    @patch.object(Book.objects, "filter")
    def test_list_borrowed_for_admin(
        self, mock_filter, MockBookSerializer, mock_perms
    ):  # Innermost first
        """Test listing all borrowed books for an admin."""
        view = BorrowedBooksListView.as_view()
        request = self._create_drf_request("get", user=self.admin_user)

        # Configure mocks
        user1 = UserFactory.build(id=10, username="borrower1")
        user2 = UserFactory.build(id=11, username="borrower2")
        # --- FIX: Add profiles for select_related ---
        # --- Use build() for profile as well if user is build() ---
        # --- Need to attach profile to user instance for the view logic ---
        user1.profile = UserProfileFactory.build(user=user1)
        user2.profile = UserProfileFactory.build(user=user2)
        mock_book1 = BookFactory.build(id=1, title="Book A", borrower=user1)
        mock_book2 = BookFactory.build(id=2, title="Book B", borrower=user2)
        mock_book3 = BookFactory.build(id=3, title="Book C", borrower=user1)
        mock_queryset = MagicMock()
        # Ensure select_related includes borrower profile for grouping logic
        mock_queryset.select_related.return_value.order_by.return_value = [
            mock_book1,
            mock_book3,
            mock_book2,
        ]
        mock_filter.return_value = mock_queryset

        # Mock the serializer to return data based on the input book
        def mock_serializer_side_effect(book, context=None, many=False):
            if many:  # Should not be called with many=True in admin case
                raise TypeError("Serializer called with many=True unexpectedly")
            # Return mock data based on book instance
            # --- FIX: Ensure context has a request for the serializer ---
            self.assertIn("request", context)
            self.assertIsInstance(context["request"], DRFRequest)
            # --- FIX: Ensure borrower has a profile for the serializer ---
            # The serializer expects book.borrower.username
            # The view logic expects book.borrower.id and book.borrower.username
            # Ensure the built borrower has these attributes accessible
            mock_data = {
                "id": book.id,
                "title": book.title,
                "borrower": book.borrower.username,
            }
            mock_instance = MagicMock()
            mock_instance.data = mock_data
            return mock_instance

        MockBookSerializer.side_effect = mock_serializer_side_effect

        # --- Call view with DRF request ---
        response = view(request)  # Pass DRF request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_filter.assert_called_once_with(available=False)
        mock_queryset.select_related.assert_called_once_with(
            "borrower", "borrower__profile"
        )
        mock_queryset.select_related.return_value.order_by.assert_called_once_with(
            "borrower__username", "due_date"
        )
        # Check serializer was called for each book
        self.assertEqual(MockBookSerializer.call_count, 3)
        # --- FIX: Check context contains DRF request ---
        MockBookSerializer.assert_any_call(mock_book1, context=ANY)
        MockBookSerializer.assert_any_call(mock_book2, context=ANY)
        MockBookSerializer.assert_any_call(mock_book3, context=ANY)
        # Verify context in one of the calls
        context_arg = MockBookSerializer.call_args_list[0].kwargs.get("context", {})
        self.assertIn("request", context_arg)
        self.assertIsInstance(context_arg["request"], DRFRequest)

        # Check response structure
        self.assertIn("borrowed_books_by_user", response.data)
        grouped_data = response.data["borrowed_books_by_user"]
        self.assertEqual(len(grouped_data), 2)  # Two borrowers

        # Check content (simplified)
        user1_data = next(g for g in grouped_data if g["borrower_name"] == "borrower1")
        user2_data = next(g for g in grouped_data if g["borrower_name"] == "borrower2")
        self.assertEqual(len(user1_data["books"]), 2)
        self.assertEqual(len(user2_data["books"]), 1)
        self.assertEqual(user1_data["books"][0]["title"], "Book A")
        self.assertEqual(user1_data["books"][1]["title"], "Book C")
        self.assertEqual(user2_data["books"][0]["title"], "Book B")


# --- Utility Views ---


class CsrfTokenViewUnitTests(ViewTestBase):
    @patch("backend.views.get_token")
    def test_csrf_token_view(self, mock_get_token):
        """Test the csrf_token_view function."""
        # Use raw factory request for function view test setup
        django_request = self.factory.get("/api/csrf/")
        # --- FIX: Add a user to the request for get_token ---
        # get_token might behave differently based on authentication status
        django_request.user = self.anonymous_user
        mock_token_value = "mockcsrftokenvalue12345"
        mock_get_token.return_value = mock_token_value

        # --- FIX: Pass the raw Django request to the view ---
        # The @api_view decorator handles wrapping it into a DRF request internally
        # before the view code runs.
        response = csrf_token_view(django_request)  # Pass raw Django request

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # --- FIX: Assert get_token was called with the underlying HttpRequest ---
        # Inside the view, `request` is the DRF Request, so `request._request` is correct.
        # The argument passed to get_token should be the original django_request.
        mock_get_token.assert_called_once_with(
            django_request
        )  # get_token needs the HttpRequest
        # Response data is DRF Response, access .data
        self.assertEqual(response.data, {"csrfToken": mock_token_value})
