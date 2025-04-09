# -*- coding: utf-8 -*-
"""
Functional tests for User Management related API views.
(UserList, CurrentUser, UserDetail, CurrentUserUpdate)
"""
from django.contrib.auth import get_user_model
from rest_framework import status

# Import the base test case and constants
from .test_views_base import LibraryAPITestCaseBase, USER_TYPE, ADMIN_TYPE
from backend.models import UserProfile # Needed for creating temp user profile

# Get the User model
User = get_user_model()

class UserViewsTestCase(LibraryAPITestCaseBase):
    """
    Tests for user management views: List, Current, Detail, Update.
    Inherits setup from LibraryAPITestCaseBase.
    """

    # --- Test User Management Views ---

    # 1. UserListView (/api/users/)
    def test_list_users_unauthenticated(self):
        """Verify unauthenticated users cannot list users."""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_user(self):
        """Verify regular users cannot list users."""
        self._login_user('user1')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_librarian(self):
        """Verify librarians cannot list users."""
        self._login_user('librarian')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_admin(self):
        """Verify admins can list users."""
        self._login_user('admin')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is a list (or paginated response)
        # Assuming no pagination for simplicity, check list type and count
        if isinstance(response.data, list): # Handle non-paginated case
            self.assertEqual(len(response.data), User.objects.count())
            usernames = [user['username'] for user in response.data]
        elif isinstance(response.data, dict) and 'results' in response.data: # Handle paginated case
            self.assertEqual(response.data['count'], User.objects.count())
            usernames = [user['username'] for user in response.data['results']]
        else:
            self.fail("Unexpected response format for user list")

        # Optionally check if specific user details are present
        self.assertIn(self.admin_user.username, usernames)
        self.assertIn(self.librarian_user.username, usernames)
        self.assertIn(self.user1.username, usernames)
        self.assertIn(self.user2.username, usernames)

    # 2. CurrentUserView (/api/users/me/)
    def test_get_current_user_unauthenticated(self):
        """Verify unauthenticated users cannot get current user details."""
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_current_user_authenticated(self):
        """Verify authenticated users can get their own details."""
        user = self._login_user('user1')
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['type'], user.profile.type)

    # 3. UserDetailView (/api/users/<id>/) - Admin Only
    def test_get_user_detail_as_admin(self):
        """Verify admin can get details of a specific user."""
        self._login_user('admin')
        target_user = self.user1
        url = self.user_detail_url(target_user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], target_user.id)
        self.assertEqual(response.data['username'], target_user.username)

    def test_update_user_detail_as_admin(self):
        """Verify admin can update details of a specific user (User fields only)."""
        self._login_user('admin')
        target_user = self.user1
        url = self.user_detail_url(target_user.id)
        update_data = {'first_name': 'UpdatedFirstName', 'email': 'updated_user1@example.com'}
        response = self.client.patch(url, update_data, format='json') # Use PATCH for partial update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_user.refresh_from_db()
        self.assertEqual(target_user.first_name, 'UpdatedFirstName')
        self.assertEqual(target_user.email, 'updated_user1@example.com')
        # Verify profile data wasn't changed (as UserSerializer profile is read-only)
        self.assertEqual(target_user.profile.age, 25)

    def test_delete_user_detail_as_admin(self):
        """Verify admin can delete a specific user."""
        self._login_user('admin')
        # Create a temporary user to delete to avoid affecting other tests
        temp_user = User.objects.create_user(username='tempdeleteuser', email='delete@me.com', password='pw')
        UserProfile.objects.create(user=temp_user, type=USER_TYPE)
        initial_count = User.objects.count()
        url = self.user_detail_url(temp_user.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), initial_count - 1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=temp_user.id)


    def test_access_user_detail_as_non_admin(self):
        """Verify non-admins cannot access user detail endpoints."""
        target_user = self.user1
        url = self.user_detail_url(target_user.id)

        # Test as regular user
        self._login_user('user2') # Login as a different user
        response_get = self.client.get(url)
        response_put = self.client.put(url, {'first_name': 'Fail'})
        response_delete = self.client.delete(url)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Test as librarian
        self._login_user('librarian')
        response_get = self.client.get(url)
        response_put = self.client.put(url, {'first_name': 'Fail'})
        response_delete = self.client.delete(url)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_detail_not_found(self):
        """Verify 404 is returned for non-existent user ID."""
        self._login_user('admin')
        non_existent_id = User.objects.latest('id').id + 99
        url = self.user_detail_url(non_existent_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # 4. CurrentUserUpdateView (/api/users/me/update/)
    def test_update_current_user_unauthenticated(self):
        """Verify unauthenticated users cannot access the update endpoint."""
        response = self.client.patch(self.current_user_update_url, {'first_name': 'Fail'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_current_user_basic_info(self):
        """Verify authenticated user can update their basic info (first_name, email)."""
        user = self._login_user('user1')
        update_data = {'first_name': 'UpdatedSelf', 'email': 'updated_self@example.com'}
        response = self.client.patch(self.current_user_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'UpdatedSelf')
        self.assertEqual(user.email, 'updated_self@example.com')
        # Check response data reflects changes
        self.assertEqual(response.data['first_name'], 'UpdatedSelf')
        self.assertEqual(response.data['email'], 'updated_self@example.com')

    def test_update_current_user_profile_info(self):
        """Verify authenticated user can update their profile info (age)."""
        user = self._login_user('user1')
        initial_age = user.profile.age
        self.assertIsNotNone(initial_age) # Ensure age is set
        # Need to send nested profile data
        update_data = {'profile': {'age': initial_age + 1}}
        response = self.client.patch(self.current_user_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        user.profile.refresh_from_db() # Refresh profile too
        self.assertEqual(user.profile.age, initial_age + 1)
        # Check response data reflects changes (profile is nested and read-only in UserSerializer,
        # but the update should have happened in the DB)
        # Let's re-fetch the user data to confirm the profile update is reflected
        response_get = self.client.get(self.current_user_url)
        self.assertEqual(response_get.data['profile']['age'], initial_age + 1)


    def test_update_current_user_password(self):
        """Verify authenticated user can update their password."""
        user = self._login_user('user1')
        update_data = {'password': 'NewSecurePassword123'}
        response = self.client.patch(self.current_user_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        # Verify password hash changed
        self.assertTrue(user.check_password('NewSecurePassword123'))
        self.assertFalse(user.check_password('password123')) # Old password should fail
        # Verify session is still valid (auth hash updated)
        response_check_again = self.client.get(self.current_user_url)
        self.assertEqual(response_check_again.status_code, status.HTTP_200_OK)


    def test_update_current_user_cannot_change_type(self):
        """
        Verify user cannot change their own profile type via this endpoint.
        NOTE: This test assumes the desired behavior is that users *cannot* change their type.
        The current implementation *might allow* this. If this test fails, it indicates
        either the test assumption is wrong or there's a potential security issue in the view/serializer.
        """
        user = self._login_user('user1')
        original_type = user.profile.type
        self.assertEqual(original_type, USER_TYPE)
        update_data = {'profile': {'type': ADMIN_TYPE}} # Attempt to become admin
        response = self.client.patch(self.current_user_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Update might succeed partially
        user.refresh_from_db()
        user.profile.refresh_from_db()
        # Assert that the type DID NOT change
        self.assertEqual(user.profile.type, original_type, "User should not be able to change their own profile type.")
        # If the type *did* change, the above assertion will fail.