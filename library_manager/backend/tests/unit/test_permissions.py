from unittest.mock import Mock
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import SAFE_METHODS

# Import your custom permission classes
from backend.views import (
    IsAdminUser,
    IsAdminOrLibrarian,
    IsAdminOrLibrarianOrReadOnly,
    IsSelfOrAdmin,
)
# Import factories to create test users
from .factories import UserFactory, UserProfileFactory

class PermissionTestBase(TestCase):
    """Base class for permission tests providing mock objects."""

    def setUp(self):
        # Create users with different roles using factories
        self.anonymous_user = AnonymousUser()
        self.regular_user = UserFactory(username='testuser')
        UserProfileFactory(user=self.regular_user, type='US')

        self.librarian_user = UserFactory(username='testlibrarian')
        UserProfileFactory(user=self.librarian_user, type='LB')

        self.admin_user = UserFactory(username='testadmin')
        UserProfileFactory(user=self.admin_user, type='AD')

        # Mock view object (usually not needed for simple permission checks)
        self.mock_view = Mock()

        # Mock request object
        self.mock_request = Mock()
        self.mock_request.method = 'GET' # Default to a safe method

    def _set_user_on_request(self, user):
        self.mock_request.user = user

# --- Test IsAdminUser ---
class IsAdminUserPermissionTests(PermissionTestBase):

    def setUp(self):
        super().setUp()
        self.permission = IsAdminUser()

    def test_admin_has_permission(self):
        self._set_user_on_request(self.admin_user)
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_librarian_does_not_have_permission(self):
        self._set_user_on_request(self.librarian_user)
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_regular_user_does_not_have_permission(self):
        self._set_user_on_request(self.regular_user)
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_anonymous_user_does_not_have_permission(self):
        self._set_user_on_request(self.anonymous_user)
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))

# --- Test IsAdminOrLibrarian ---
class IsAdminOrLibrarianPermissionTests(PermissionTestBase):
    def setUp(self):
        super().setUp()
        self.permission = IsAdminOrLibrarian()

    def test_admin_has_permission(self):
        self._set_user_on_request(self.admin_user)
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_librarian_has_permission(self):
        self._set_user_on_request(self.librarian_user)
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_regular_user_does_not_have_permission(self):
        self._set_user_on_request(self.regular_user)
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))

    def test_anonymous_user_does_not_have_permission(self):
        self._set_user_on_request(self.anonymous_user)
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))


# --- Test IsAdminOrLibrarianOrReadOnly ---
class IsAdminOrLibrarianOrReadOnlyPermissionTests(PermissionTestBase):
    def setUp(self):
        super().setUp()
        self.permission = IsAdminOrLibrarianOrReadOnly()
        self.mock_obj = Mock() # For has_object_permission

    def test_safe_method_allowed_for_regular_user(self):
        self._set_user_on_request(self.regular_user)
        self.mock_request.method = 'GET'
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))
        self.assertTrue(self.permission.has_object_permission(self.mock_request, self.mock_view, self.mock_obj))

    def test_unsafe_method_denied_for_regular_user(self):
        self._set_user_on_request(self.regular_user)
        self.mock_request.method = 'POST'
        self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))
        self.assertFalse(self.permission.has_object_permission(self.mock_request, self.mock_view, self.mock_obj))

    def test_unsafe_method_allowed_for_librarian(self):
        self._set_user_on_request(self.librarian_user)
        self.mock_request.method = 'PUT'
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))
        self.assertTrue(self.permission.has_object_permission(self.mock_request, self.mock_view, self.mock_obj))

    def test_unsafe_method_allowed_for_admin(self):
        self._set_user_on_request(self.admin_user)
        self.mock_request.method = 'DELETE'
        self.assertTrue(self.permission.has_permission(self.mock_request, self.mock_view))
        self.assertTrue(self.permission.has_object_permission(self.mock_request, self.mock_view, self.mock_obj))

    def test_any_method_denied_for_anonymous(self):
        self._set_user_on_request(self.anonymous_user)
        for method in SAFE_METHODS + ('POST', 'PUT', 'DELETE'):
             self.mock_request.method = method
             self.assertFalse(self.permission.has_permission(self.mock_request, self.mock_view))
             self.assertFalse(self.permission.has_object_permission(self.mock_request, self.mock_view, self.mock_obj))


# --- Test IsSelfOrAdmin ---
class IsSelfOrAdminPermissionTests(PermissionTestBase):
    def setUp(self):
        super().setUp()
        self.permission = IsSelfOrAdmin()
        # Create another user for object permission checks
        self.other_user = UserFactory(username='otheruser')
        UserProfileFactory(user=self.other_user, type='US')


    def test_admin_can_access_other_user_object(self):
        self._set_user_on_request(self.admin_user)
        # The object being accessed is self.other_user
        self.assertTrue(self.permission.has_object_permission(self.mock_request, self.mock_view, self.other_user))

    def test_regular_user_can_access_own_object(self):
        self._set_user_on_request(self.regular_user)
        # The object being accessed is self.regular_user
        self.assertTrue(self.permission.has_object_permission(self.mock_request, self.mock_view, self.regular_user))

    def test_regular_user_cannot_access_other_user_object(self):
        self._set_user_on_request(self.regular_user)
        # The object being accessed is self.other_user
        self.assertFalse(self.permission.has_object_permission(self.mock_request, self.mock_view, self.other_user))

    def test_anonymous_user_cannot_access_any_object(self):
        self._set_user_on_request(self.anonymous_user)
        self.assertFalse(self.permission.has_object_permission(self.mock_request, self.mock_view, self.regular_user))
        self.assertFalse(self.permission.has_object_permission(self.mock_request, self.mock_view, self.other_user))