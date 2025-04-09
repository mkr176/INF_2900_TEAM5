# -*- coding: utf-8 -*-
"""
Functional tests for Utility API views (e.g., CSRF token).
"""
from rest_framework import status

# Import the base test case
from .test_views_base import LibraryAPITestCaseBase

class UtilityViewsTestCase(LibraryAPITestCaseBase):
    """
    Tests for utility views like CSRF token endpoint.
    Inherits setup from LibraryAPITestCaseBase.
    """

    # --- Test CSRF Token View ---
    def test_get_csrf_token(self):
        """Ensure anyone can get a CSRF token."""
        response = self.client.get(self.csrf_token_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', response.data)
        self.assertIsNotNone(response.data['csrfToken'])