from django.test import TestCase, Client
from django.urls import reverse

class MyViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        # Request the root URL.  This will be caught by the catch-all route.
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'startpage.html')


    def test_server_running(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    # Add more tests for other views, including POST requests, etc.
    # Test different scenarios, including error cases.