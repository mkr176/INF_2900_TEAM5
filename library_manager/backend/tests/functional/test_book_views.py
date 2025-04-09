# -*- coding: utf-8 -*-
"""
Functional tests for Book Management related API views.
(BookListCreateView, BookDetailView)
Excludes borrow/return functionality.
"""
from rest_framework import status

# Import the base test case and constants/models
from .test_views_base import (
    LibraryAPITestCaseBase,
    TEST_BOOK_ISBN, TEST_BOOK_ISBN_2, TEST_BOOK_ISBN_3,
    TEST_BOOK_ISBN_4, TEST_BOOK_ISBN_5
)
from backend.models import Book

class BookViewsTestCase(LibraryAPITestCaseBase):
    """
    Tests for book management views: List, Create, Retrieve, Update, Delete.
    Inherits setup from LibraryAPITestCaseBase.
    """

    # --- Test BookListCreateView (/api/books/) - List Tests ---
    def test_list_books_unauthenticated(self):
        """Verify unauthenticated users cannot list books (expect 403)."""
        response = self.client.get(self.book_list_create_url)
        # Based on IsAdminOrLibrarianOrReadOnly, unauthenticated should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books_authenticated_user(self):
        """Verify regular authenticated users can list books."""
        self._login_user('user1')
        response = self.client.get(self.book_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response contains expected books (adjust count based on setup)
        # Assuming no pagination for simplicity
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), Book.objects.count())
            titles = [book['title'] for book in response.data]
        elif isinstance(response.data, dict) and 'results' in response.data: # Handle pagination
            self.assertEqual(response.data['count'], Book.objects.count())
            titles = [book['title'] for book in response.data['results']]
        else:
             self.fail("Unexpected response format for book list")

        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)
        self.assertIn(self.borrowed_book.title, titles)

    def test_list_books_authenticated_librarian(self):
        """Verify librarian authenticated users can list books."""
        self._login_user('librarian')
        response = self.client.get(self.book_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Basic check, content verified in user test

    def test_list_books_authenticated_admin(self):
        """Verify admin authenticated users can list books."""
        self._login_user('admin')
        response = self.client.get(self.book_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Basic check, content verified in user test

    # --- Test BookListCreateView (/api/books/) - Create Tests ---
    def test_create_book_unauthenticated(self):
        """Verify unauthenticated users cannot create books."""
        book_data = {
            'title': 'Unauthorized Creation', 'author': 'Anon', 'isbn': '999-0-00-000000-0',
            'category': 'TXT', 'language': 'Klingon', 'condition': 'NW'
        }
        response = self.client.post(self.book_list_create_url, book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_user(self):
        """Verify regular users cannot create books."""
        self._login_user('user1')
        book_data = {
            'title': 'User Creation Attempt', 'author': 'User', 'isbn': '999-0-00-000000-1',
            'category': 'TXT', 'language': 'Esperanto', 'condition': 'NW'
        }
        response = self.client.post(self.book_list_create_url, book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_librarian(self):
        """Verify librarians can create books."""
        user = self._login_user('librarian')
        initial_book_count = Book.objects.count()
        book_data = {
            'title': 'Librarian Added Book', 'author': 'Lib Author', 'isbn': TEST_BOOK_ISBN_4,
            'category': 'ROM', 'language': 'French', 'condition': 'GD', 'publication_year': 2023
        }
        response = self.client.post(self.book_list_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), initial_book_count + 1)
        new_book = Book.objects.get(isbn=TEST_BOOK_ISBN_4)
        self.assertEqual(new_book.title, book_data['title'])
        self.assertEqual(new_book.added_by, user) # Verify added_by is set correctly
        self.assertTrue(new_book.available) # Should default to available

    def test_create_book_as_admin(self):
        """Verify admins can create books."""
        user = self._login_user('admin')
        initial_book_count = Book.objects.count()
        # Use a different ISBN to avoid conflict with librarian test if run together
        admin_isbn = '978-9-99-999999-9'
        book_data = {
            'title': 'Admin Added Book', 'author': 'Admin Author', 'isbn': admin_isbn,
            'category': 'HIS', 'language': 'German', 'condition': 'PO', 'publication_year': 1999
        }
        response = self.client.post(self.book_list_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), initial_book_count + 1)
        new_book = Book.objects.get(isbn=admin_isbn)
        self.assertEqual(new_book.title, book_data['title'])
        self.assertEqual(new_book.added_by, user) # Verify added_by is set correctly

    def test_create_book_missing_fields(self):
        """Verify creating a book with missing required fields fails."""
        self._login_user('librarian')
        # Missing title
        book_data_no_title = {
            'author': 'No Title Author', 'isbn': '999-0-00-000000-2',
            'category': 'SF', 'language': 'English', 'condition': 'GD'
        }
        response = self.client.post(self.book_list_create_url, book_data_no_title, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

        # Missing isbn
        book_data_no_isbn = {
            'title': 'No ISBN Book', 'author': 'No ISBN Author',
            'category': 'SF', 'language': 'English', 'condition': 'GD'
        }
        response = self.client.post(self.book_list_create_url, book_data_no_isbn, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('isbn', response.data)
        # Add checks for other required fields (author, category, language, condition) if necessary

    def test_create_book_invalid_data(self):
        """Verify creating a book with invalid data (e.g., bad category) fails."""
        self._login_user('librarian')
        book_data_invalid_category = {
            'title': 'Invalid Category Book', 'author': 'Invalid Author', 'isbn': '999-0-00-000000-3',
            'category': 'INVALID', # Not in choices
            'language': 'English', 'condition': 'GD'
        }
        response = self.client.post(self.book_list_create_url, book_data_invalid_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

        book_data_invalid_condition = {
            'title': 'Invalid Condition Book', 'author': 'Invalid Author', 'isbn': '999-0-00-000000-4',
            'category': 'SF', 'language': 'English',
            'condition': 'EXCELLENT' # Not in choices
        }
        response = self.client.post(self.book_list_create_url, book_data_invalid_condition, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('condition', response.data)

    def test_create_book_duplicate_isbn(self):
        """Verify creating a book with an existing ISBN fails."""
        self._login_user('librarian')
        book_data_duplicate_isbn = {
            'title': 'Duplicate ISBN Book', 'author': 'Duplicate Author',
            'isbn': self.book1.isbn, # Use existing ISBN
            'category': 'SF', 'language': 'English', 'condition': 'GD'
        }
        response = self.client.post(self.book_list_create_url, book_data_duplicate_isbn, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('isbn', response.data) # Expecting error related to unique constraint

    # --- Test BookListCreateView (/api/books/) - List Filtering/Searching/Ordering Tests ---
    def test_list_books_filtering_category(self):
        """Verify filtering books by category."""
        self._login_user('user1')
        # Filter for Science Fiction (SF) - should match book1
        response = self.client.get(self.book_list_create_url, {'category': 'SF'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.book1.title)

        # Filter for History (HIS) - should match book2
        response = self.client.get(self.book_list_create_url, {'category': 'HIS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.book2.title)

    def test_list_books_filtering_language(self):
        """Verify filtering books by language."""
        self._login_user('user1')
        # Filter for English - should match book1, borrowed_book, book_for_filter
        response = self.client.get(self.book_list_create_url, {'language': 'English'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 3)
        titles = {book['title'] for book in data}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.borrowed_book.title, titles)
        self.assertIn(self.book_for_filter.title, titles)

        # Filter for Spanish - should match book2
        response = self.client.get(self.book_list_create_url, {'language': 'Spanish'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.book2.title)

    def test_list_books_filtering_available(self):
        """Verify filtering books by availability."""
        self._login_user('user1')
        # Filter for available=True - should match book1, book2, book_for_filter
        response = self.client.get(self.book_list_create_url, {'available': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 3)
        titles = {book['title'] for book in data}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)
        self.assertIn(self.book_for_filter.title, titles)

        # Filter for available=False - should match borrowed_book
        response = self.client.get(self.book_list_create_url, {'available': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.borrowed_book.title)

    def test_list_books_filtering_condition(self):
        """Verify filtering books by condition."""
        self._login_user('user1')
        # Filter for Good (GD) - should match book1, book_for_filter
        response = self.client.get(self.book_list_create_url, {'condition': 'GD'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)
        titles = {book['title'] for book in data}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book_for_filter.title, titles)

    def test_list_books_searching_title(self):
        """Verify searching books by title."""
        self._login_user('user1')
        # Search for "Test" - should match book1, book2
        response = self.client.get(self.book_list_create_url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)
        titles = {book['title'] for book in data}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)

        # Search for "Crime" - should match book_for_filter
        response = self.client.get(self.book_list_create_url, {'search': 'Crime'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.book_for_filter.title)

    def test_list_books_searching_author(self):
        """Verify searching books by author."""
        self._login_user('user1')
        # Search for "Author One" - should match book1, book_for_filter
        response = self.client.get(self.book_list_create_url, {'search': 'Author One'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)
        titles = {book['title'] for book in data}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book_for_filter.title, titles)

    def test_list_books_searching_isbn(self):
        """Verify searching books by ISBN."""
        self._login_user('user1')
        # Search for specific ISBN of book1
        response = self.client.get(self.book_list_create_url, {'search': TEST_BOOK_ISBN})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['isbn'], self.book1.isbn)

    def test_list_books_ordering_title(self):
        """Verify ordering books by title."""
        self._login_user('user1')
        response = self.client.get(self.book_list_create_url, {'ordering': 'title'}) # Ascending
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        titles = [book['title'] for book in data]
        self.assertEqual(titles, sorted(titles)) # Check if sorted alphabetically

        response = self.client.get(self.book_list_create_url, {'ordering': '-title'}) # Descending
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        titles_desc = [book['title'] for book in data]
        self.assertEqual(titles_desc, sorted(titles, reverse=True)) # Check if sorted reverse alphabetically

    def test_list_books_ordering_publication_year(self):
        """Verify ordering books by publication year."""
        self._login_user('user1')
        response = self.client.get(self.book_list_create_url, {'ordering': 'publication_year'}) # Ascending
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        years = [book['publication_year'] for book in data if book['publication_year'] is not None]
        self.assertEqual(years, sorted(years)) # Check if sorted numerically

        response = self.client.get(self.book_list_create_url, {'ordering': '-publication_year'}) # Descending
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        years_desc = [book['publication_year'] for book in data if book['publication_year'] is not None]
        self.assertEqual(years_desc, sorted(years, reverse=True)) # Check if sorted reverse numerically


    # --- Test BookDetailView (/api/books/<id>/) ---

    # Retrieve (GET)
    def test_get_book_detail_unauthenticated(self):
        """Verify unauthenticated users cannot retrieve book details."""
        url = self.book_detail_url(self.book1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_book_detail_authenticated_user(self):
        """Verify authenticated users can retrieve book details."""
        self._login_user('user1')
        url = self.book_detail_url(self.book1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book1.id)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['isbn'], self.book1.isbn)
        # Check derived fields are present
        self.assertIn('category_display', response.data)
        self.assertIn('condition_display', response.data)
        self.assertIn('days_left', response.data) # Will be null for available book

    def test_get_book_detail_not_found(self):
        """Verify 404 is returned for non-existent book ID."""
        self._login_user('user1')
        non_existent_id = Book.objects.latest('id').id + 99
        url = self.book_detail_url(non_existent_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Update (PUT/PATCH)
    def test_update_book_unauthenticated(self):
        """Verify unauthenticated users cannot update books."""
        url = self.book_detail_url(self.book1.id)
        update_data = {'title': 'Updated Title Fail'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(url, update_data, format='json') # PUT requires all fields usually
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_user(self):
        """Verify regular users cannot update books."""
        self._login_user('user1')
        url = self.book_detail_url(self.book1.id)
        update_data = {'title': 'User Update Attempt'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Also test PUT
        # Need full data for PUT, get existing data first
        get_response = self.client.get(url)
        full_data = get_response.data
        full_data['title'] = 'User Update Attempt PUT'
        # Remove read-only fields before PUT
        read_only_fields = ['added_by', 'borrower', 'borrower_id', 'added_by_id',
                            'category_display', 'condition_display', 'days_left',
                            'overdue', 'days_overdue', 'due_today', 'available',
                            'borrow_date', 'due_date']
        for field in read_only_fields:
            if field in full_data:
                del full_data[field]

        response_put = self.client.put(url, full_data, format='json')
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)


    def test_update_book_as_librarian(self):
        """Verify librarians can update books (e.g., title, condition)."""
        self._login_user('librarian')
        url = self.book_detail_url(self.book1.id)
        update_data = {'title': 'Updated by Librarian', 'condition': 'FR'} # Change title and condition
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated by Librarian')
        self.assertEqual(self.book1.condition, 'FR')
        # Check response reflects changes
        self.assertEqual(response.data['title'], 'Updated by Librarian')
        self.assertEqual(response.data['condition'], 'FR')
        self.assertEqual(response.data['condition_display'], 'Fair') # Check display field updated

    def test_update_book_as_admin(self):
        """Verify admins can update books."""
        self._login_user('admin')
        url = self.book_detail_url(self.book2.id)
        update_data = {'language': 'Latin', 'publication_year': 2025}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book2.refresh_from_db()
        self.assertEqual(self.book2.language, 'Latin')
        self.assertEqual(self.book2.publication_year, 2025)
        self.assertEqual(response.data['language'], 'Latin')
        self.assertEqual(response.data['publication_year'], 2025)

    def test_update_book_cannot_change_availability_directly(self):
        """Verify 'available' field cannot be changed via PATCH/PUT (should use borrow/return)."""
        self._login_user('librarian')
        url = self.book_detail_url(self.book1.id)
        self.assertTrue(self.book1.available) # Starts available
        update_data = {'available': False} # Attempt to make unavailable
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Update might succeed partially
        self.book1.refresh_from_db()
        # Assert that 'available' DID NOT change because it's read-only in serializer
        self.assertTrue(self.book1.available, "Availability should not change via direct update.")
        # Check response data also shows original value
        self.assertTrue(response.data['available'])

    def test_update_book_invalid_data(self):
        """Verify updating a book with invalid data fails."""
        self._login_user('librarian')
        url = self.book_detail_url(self.book1.id)
        update_data = {'category': 'INVALID'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    # Delete (DELETE)
    def test_delete_book_unauthenticated(self):
        """Verify unauthenticated users cannot delete books."""
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_as_user(self):
        """Verify regular users cannot delete books."""
        self._login_user('user1')
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_as_librarian(self):
        """Verify librarians can delete books."""
        self._login_user('librarian')
        # Use book_for_filter to avoid affecting other tests too much
        target_book = self.book_for_filter
        url = self.book_detail_url(target_book.id)
        initial_book_count = Book.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), initial_book_count - 1)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=target_book.id)

    def test_delete_book_as_admin(self):
        """Verify admins can delete books."""
        self._login_user('admin')
        # Create a temporary book to delete
        temp_book = Book.objects.create(title='Temp Delete', author='Temp', isbn='999-9-99-999999-0', category='TXT', language='None', condition='PO')
        url = self.book_detail_url(temp_book.id)
        initial_book_count = Book.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), initial_book_count - 1)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=temp_book.id)

    def test_delete_book_not_found(self):
        """Verify deleting a non-existent book returns 404."""
        self._login_user('admin')
        non_existent_id = Book.objects.latest('id').id + 99
        url = self.book_detail_url(non_existent_id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)