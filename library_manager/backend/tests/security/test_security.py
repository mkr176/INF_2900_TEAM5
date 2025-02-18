# from django.test import TestCase, Client
# from django.urls import reverse

## for we are not yet testing the CSRF protection
# class SecurityTests(TestCase):
#     def setUp(self):
#         self.client = Client()

#     def test_csrf_protection(self):
#         # Correct the reverse call, similar to above.
#         response = self.client.post(reverse('signup'), {})  # Use the 'signup' URL name
#         self.assertEqual(response.status_code, 403)  # Expect Forbidden (due to CSRF)

#         # To properly test CSRF, you'd need to get a CSRF token first,
#         # then include it in the POST request.  This is a more advanced test.
#         # For now, testing for the 403 is a good start.