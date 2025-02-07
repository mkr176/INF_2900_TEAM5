from django.test import TestCase, Client
from django.urls import reverse

class MyViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('frontend:front'))  # Use reverse to get the URL
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'startpage.html')  # Check the correct template

    # Add more tests for other views, including POST requests, etc.
    # Test different scenarios, including error cases.