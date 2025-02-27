from django.test import TestCase, Client
from django.urls import reverse

class MyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')  # Assuming you have a URL named 'index'

    def test_index_view(self):
        """Test that the index view returns a 200 status code and uses the correct template."""
        # Request the root URL.  This will be caught by the catch-all route.
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'startpage.html')


    def test_server_running(self):
        """Test that the server is running and returns a 200 status code for the index view."""
        response = self.client.get(self.index_url) #use the index_url
        self.assertEqual(response.status_code, 200)
    # Add more tests for other views, including POST requests, etc.
    # Test different scenarios, including error cases.