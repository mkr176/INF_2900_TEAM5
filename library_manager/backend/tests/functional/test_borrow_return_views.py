# -*- coding: utf-8 -*-
"""
Functional tests for Book Borrowing, Returning, and Listing Borrowed Books API views.
(BorrowBookView, ReturnBookView, BorrowedBooksListView)
"""
from datetime import date, timedelta
from rest_framework import status

# Import the base test case and constants/models
from .test_views_base import LibraryAPITestCaseBase, USER_TYPE, ADMIN_TYPE, LIBRARIAN_TYPE
from backend.models import Book
from backend.views import MAX_BORROW_LIMIT # Import borrow limit

class BorrowReturnViewsTestCase(LibraryAPITestCaseBase):
    """
    Tests for book borrowing, returning, and listing borrowed books.
    Inherits setup from LibraryAPITestCaseBase.
    """

    # --- Test BorrowBookView (/api/books/<book_id>/borrow/) ---

    def test_borrow_book_unauthenticated(self):
        """Verify unauthenticated users cannot borrow books."""
        url = self.book_borrow_url(self.book1.id) # book1 is initially available
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrow_book_success(self):
        """Verify an authenticated user can borrow an available book."""
        user = self._login_user('user2') # user2 has no books borrowed initially
        book_to_borrow = self.book1
        url = self.book_borrow_url(book_to_borrow.id)

        self.assertTrue(book_to_borrow.available) # Ensure book is available
        self.assertIsNone(book_to_borrow.borrower)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('book', response.data)
        self.assertEqual(response.data['book']['id'], book_to_borrow.id)
        self.assertEqual(response.data['book']['borrower'], user.username) # Serializer shows username

        # Verify database state
        book_to_borrow.refresh_from_db()
        self.assertFalse(book_to_borrow.available)
        self.assertEqual(book_to_borrow.borrower, user)
        self.assertEqual(book_to_borrow.borrow_date, date.today())
        self.assertEqual(book_to_borrow.due_date, date.today() + timedelta(weeks=2))

    def test_borrow_book_already_borrowed(self):
        """Verify a user cannot borrow a book that is already checked out."""
        self._login_user('user2') # user2 tries to borrow
        book_already_borrowed = self.borrowed_book # Borrowed by user1 in setup
        url = self.book_borrow_url(book_already_borrowed.id)

        self.assertFalse(book_already_borrowed.available) # Ensure it's not available

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('unavailable', response.data['error']) # Check for specific error message part

        # Verify book state hasn't changed
        book_already_borrowed.refresh_from_db()
        self.assertEqual(book_already_borrowed.borrower, self.user1) # Still borrowed by user1

    def test_borrow_book_limit_reached(self):
        """Verify a user cannot borrow more books than the limit."""
        user = self._login_user('user1') # user1 already has 1 book (borrowed_book)

        # Borrow books up to the limit - 1
        # Create MAX_BORROW_LIMIT - 1 more available books
        available_books = []
        for i in range(MAX_BORROW_LIMIT - 1):
             book = Book.objects.create(
                 title=f'Limit Test Book {i+1}', author='Limit Author',
                 isbn=f'998-0-00-00000{i}-0', category='TXT', language='Test', condition='NW'
             )
             available_books.append(book)
             # Borrow the book
             url_borrow = self.book_borrow_url(book.id)
             response_borrow = self.client.post(url_borrow)
             self.assertEqual(response_borrow.status_code, status.HTTP_200_OK, f"Failed to borrow book {i+1}")

        # Verify user is now at the limit
        current_borrow_count = Book.objects.filter(borrower=user, available=False).count()
        self.assertEqual(current_borrow_count, MAX_BORROW_LIMIT)

        # Attempt to borrow one more book (book2 is available)
        url_limit_exceed = self.book_borrow_url(self.book2.id)
        response_limit = self.client.post(url_limit_exceed)

        self.assertEqual(response_limit.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_limit.data)
        self.assertIn('limit reached', response_limit.data['error'].lower())

        # Clean up extra books created for this test
        for book in available_books:
            book.delete()

    def test_borrow_book_not_found(self):
        """Verify borrowing a non-existent book returns 404."""
        self._login_user('user1')
        non_existent_id = Book.objects.latest('id').id + 99
        url = self.book_borrow_url(non_existent_id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # --- Test ReturnBookView (/api/books/<book_id>/return/) ---

    def test_return_book_unauthenticated(self):
        """Verify unauthenticated users cannot return books."""
        url = self.book_return_url(self.borrowed_book.id) # borrowed_book is borrowed by user1
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_return_book_success_by_borrower(self):
        """Verify the user who borrowed the book can return it."""
        user = self._login_user('user1') # user1 borrowed 'borrowed_book'
        book_to_return = self.borrowed_book
        url = self.book_return_url(book_to_return.id)

        self.assertFalse(book_to_return.available) # Ensure it's borrowed
        self.assertEqual(book_to_return.borrower, user)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('book', response.data)
        self.assertTrue(response.data['book']['available'])
        self.assertIsNone(response.data['book']['borrower'])

        # Verify database state
        book_to_return.refresh_from_db()
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)
        self.assertIsNone(book_to_return.borrow_date)
        self.assertIsNone(book_to_return.due_date)

    def test_return_book_success_by_admin(self):
        """Verify an admin can return a book borrowed by another user."""
        admin = self._login_user('admin')
        book_to_return = self.borrowed_book # Borrowed by user1
        url = self.book_return_url(book_to_return.id)

        self.assertFalse(book_to_return.available)
        self.assertEqual(book_to_return.borrower, self.user1) # Borrowed by user1

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify database state
        book_to_return.refresh_from_db()
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)

    def test_return_book_success_by_librarian(self):
        """Verify a librarian can return a book borrowed by another user."""
        librarian = self._login_user('librarian')
        book_to_return = self.borrowed_book # Borrowed by user1
        url = self.book_return_url(book_to_return.id)

        self.assertFalse(book_to_return.available)
        self.assertEqual(book_to_return.borrower, self.user1) # Borrowed by user1

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify database state
        book_to_return.refresh_from_db()
        self.assertTrue(book_to_return.available)
        self.assertIsNone(book_to_return.borrower)

    def test_return_book_not_borrowed_by_user(self):
        """Verify a user cannot return a book they did not borrow."""
        user = self._login_user('user2') # user2 did not borrow 'borrowed_book'
        book_to_return = self.borrowed_book # Borrowed by user1
        url = self.book_return_url(book_to_return.id)

        self.assertFalse(book_to_return.available)
        self.assertEqual(book_to_return.borrower, self.user1)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Forbidden action
        self.assertIn('error', response.data)
        self.assertIn('did not borrow', response.data['error'])

        # Verify book state hasn't changed
        book_to_return.refresh_from_db()
        self.assertFalse(book_to_return.available)
        self.assertEqual(book_to_return.borrower, self.user1)

    def test_return_book_already_available(self):
        """Verify returning a book that is already available results in an error."""
        user = self._login_user('user1')
        book_available = self.book1 # book1 is available
        url = self.book_return_url(book_available.id)

        self.assertTrue(book_available.available)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('already available', response.data['error'])

    def test_return_book_not_found(self):
        """Verify returning a non-existent book returns 404."""
        self._login_user('user1')
        non_existent_id = Book.objects.latest('id').id + 99
        url = self.book_return_url(non_existent_id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # --- Test BorrowedBooksListView (/api/books/borrowed/) ---

    def test_list_borrowed_books_unauthenticated(self):
        """Verify unauthenticated users cannot list borrowed books."""
        response = self.client.get(self.borrowed_books_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_borrowed_books_user(self):
        """Verify a regular user sees only their borrowed books."""
        user = self._login_user('user1') # user1 has 'borrowed_book'
        # Borrow another book for user1 to have multiple
        book_to_borrow = self.book1
        borrow_url = self.book_borrow_url(book_to_borrow.id)
        self.client.post(borrow_url) # Borrow book1
        book_to_borrow.refresh_from_db()

        response = self.client.get(self.borrowed_books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_borrowed_books', response.data)

        borrowed_list = response.data['my_borrowed_books']
        self.assertIsInstance(borrowed_list, list)
        self.assertEqual(len(borrowed_list), 2) # borrowed_book + book1

        titles = {book['title'] for book in borrowed_list}
        self.assertIn(self.borrowed_book.title, titles)
        self.assertIn(book_to_borrow.title, titles)

        # Check for derived fields (e.g., days_left)
        for book_data in borrowed_list:
            self.assertIn('days_left', book_data)
            self.assertIsNotNone(book_data['days_left'])
            self.assertIn('overdue', book_data)
            self.assertIn('days_overdue', book_data)
            self.assertIn('due_today', book_data)
            self.assertEqual(book_data['borrower'], user.username) # Check borrower is correct

        # Return the extra borrowed book
        return_url = self.book_return_url(book_to_borrow.id)
        self.client.post(return_url)

    def test_list_borrowed_books_admin(self):
        """Verify an admin sees all borrowed books, grouped by user."""
        self._login_user('admin')
        # Ensure there are books borrowed by different users
        # user1 has borrowed_book
        # Borrow book1 for user2
        self.client.force_login(self.user2)
        borrow_url_user2 = self.book_borrow_url(self.book1.id)
        self.client.post(borrow_url_user2)
        self.client.force_login(self.admin_user) # Log back in as admin

        response = self.client.get(self.borrowed_books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('borrowed_books_by_user', response.data)

        grouped_data = response.data['borrowed_books_by_user']
        self.assertIsInstance(grouped_data, list)
        # Should have entries for user1 and user2
        self.assertEqual(len(grouped_data), 2)

        user1_entry = next((item for item in grouped_data if item['borrower_name'] == self.user1.username), None)
        user2_entry = next((item for item in grouped_data if item['borrower_name'] == self.user2.username), None)

        self.assertIsNotNone(user1_entry)
        self.assertIsNotNone(user2_entry)

        self.assertEqual(user1_entry['borrower_id'], self.user1.id)
        self.assertIsInstance(user1_entry['books'], list)
        self.assertEqual(len(user1_entry['books']), 1)
        self.assertEqual(user1_entry['books'][0]['title'], self.borrowed_book.title)
        self.assertIn('days_left', user1_entry['books'][0]) # Check derived fields

        self.assertEqual(user2_entry['borrower_id'], self.user2.id)
        self.assertIsInstance(user2_entry['books'], list)
        self.assertEqual(len(user2_entry['books']), 1)
        self.assertEqual(user2_entry['books'][0]['title'], self.book1.title)
        self.assertIn('days_left', user2_entry['books'][0]) # Check derived fields

        # Clean up: return book borrowed by user2
        self.client.force_login(self.admin_user) # Ensure still admin
        return_url_user2 = self.book_return_url(self.book1.id)
        self.client.post(return_url_user2)


    def test_list_borrowed_books_librarian(self):
        """Verify a librarian sees all borrowed books, grouped by user."""
        self._login_user('librarian')
        # Similar setup and checks as admin test
        # user1 has borrowed_book
        # Borrow book1 for user2
        self.client.force_login(self.user2)
        borrow_url_user2 = self.book_borrow_url(self.book1.id)
        self.client.post(borrow_url_user2)
        self.client.force_login(self.librarian_user) # Log back in as librarian

        response = self.client.get(self.borrowed_books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('borrowed_books_by_user', response.data)

        grouped_data = response.data['borrowed_books_by_user']
        self.assertIsInstance(grouped_data, list)
        self.assertEqual(len(grouped_data), 2) # user1 and user2

        user1_entry = next((item for item in grouped_data if item['borrower_name'] == self.user1.username), None)
        user2_entry = next((item for item in grouped_data if item['borrower_name'] == self.user2.username), None)

        self.assertIsNotNone(user1_entry)
        self.assertIsNotNone(user2_entry)
        self.assertEqual(len(user1_entry['books']), 1)
        self.assertEqual(user1_entry['books'][0]['title'], self.borrowed_book.title)
        self.assertEqual(len(user2_entry['books']), 1)
        self.assertEqual(user2_entry['books'][0]['title'], self.book1.title)

        # Clean up: return book borrowed by user2
        self.client.force_login(self.librarian_user) # Ensure still librarian
        return_url_user2 = self.book_return_url(self.book1.id)
        self.client.post(return_url_user2)

    def test_list_borrowed_books_no_books_borrowed(self):
        """Verify the list is empty when the user has no borrowed books."""
        self._login_user('user2') # user2 has no books borrowed initially
        response = self.client.get(self.borrowed_books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_borrowed_books', response.data)
        self.assertEqual(len(response.data['my_borrowed_books']), 0)