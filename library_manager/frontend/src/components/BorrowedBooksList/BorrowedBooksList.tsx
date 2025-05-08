// library_manager\frontend\src\components\BorrowedBooksList\BorrowedBooksList.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
// <<< ADD: Import shared types >>>
import { Book } from '../../types/models';
import "./BorrowedBooksList.css";
import BookCard from '../BookCard/BookCard';
// --- Interface Updates ---
// <<< REMOVE: Local Book interface definition >>>
// interface Book { ... }

// <<< MODIFY: Define BorrowedBooksGroup locally using imported Book type >>>
interface BorrowedBooksGroup {
    borrower_id: number;
    borrower_name: string;
    books: Book[];
}

// User interface might not be strictly needed here if only using currentUser from context
// interface User { ... }

interface BorrowedBooksListProps {}

// <<< ADD: Default book image URL (must match backend/serializer) >>>
const DEFAULT_BOOK_IMAGE_URL = "/static/images/library_seal.jpg";

const BorrowedBooksList: React.FC<BorrowedBooksListProps> = () => {
    const { currentUser, getCSRFToken } = useAuth();
    const [borrowedData, setBorrowedData] = useState<Book[] | BorrowedBooksGroup[] | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Determine if the user has special privileges (Admin or Librarian)
    const isPrivilegedUser = currentUser?.profile?.type === "AD" || currentUser?.profile?.type === "LB";

    const fetchBorrowedBooks = useCallback(async () => {
        // No need to check currentUser here, as the hook ensures it's available or null
        // If currentUser is null, isPrivilegedUser will be false, and the API call might return data accordingly (e.g., empty list or error handled by backend)
        // However, it's good practice to ensure currentUser exists before fetching user-specific data if the API requires authentication.
        // Let's assume the API endpoint handles unauthenticated requests gracefully or requires login (which useAuth should manage).

        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/books/borrowed/', { credentials: 'include' }); // Ensure cookies are sent
            if (!response.ok) {
                // Handle specific errors like 401 Unauthorized or 403 Forbidden
                if (response.status === 401 || response.status === 403) {
                    throw new Error('Authentication required. Please log in.');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Borrowed books data fetched:", data);

            // Set state based on the expected structure from the API response
            if (isPrivilegedUser) {
                // Expecting { borrowed_books_by_user: BorrowedBooksGroup[] }
                const groupedData: BorrowedBooksGroup[] = data.borrowed_books_by_user || [];
                setBorrowedData(groupedData);
            } else {
                // Expecting { my_borrowed_books: Book[] }
                const flatData: Book[] = data.my_borrowed_books || [];
                setBorrowedData(flatData);
            }
        } catch (err: any) {
            console.error('Error fetching borrowed books:', err);
            setError(err.message || 'Failed to load borrowed books.');
            setBorrowedData(null); // Clear data on error
        } finally {
            setIsLoading(false);
        }
    }, [isPrivilegedUser]); // Depend on currentUser and derived isPrivilegedUser

    useEffect(() => {
        // Fetch only if a user is logged in, otherwise, show appropriate message
        if (currentUser) {
            fetchBorrowedBooks();
        } else {
            setIsLoading(false);
            setError("Please log in to view borrowed books.");
            setBorrowedData(null);
        }
    }, [fetchBorrowedBooks, currentUser]); // Rerun effect if currentUser changes

    const handleReturnBook = async (bookId: number) => {
        // Confirmation dialog
        if (!window.confirm("Are you sure you want to return this book?")) return;

        // Get CSRF token
        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Error: Could not verify security token. Please refresh and try again.");
            return;
        }

        try {
            const response = await fetch(`/api/books/${bookId}/return/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include', // Send cookies
            });

            if (!response.ok) {
                // Try to parse error message from backend
                let errorDetail = `Failed to return book: HTTP status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.error || errorData.detail || errorDetail;
                } catch (e) { /* Ignore parsing error */ }
                throw new Error(errorDetail);
            }

            // Success
            const result = await response.json();
            alert(result.message || 'Book returned successfully!');
            fetchBorrowedBooks(); // Refresh the list after successful return
        } catch (error: any) {
            console.error("Error returning book:", error);
            alert(`Error returning book: ${error.message}`);
        }
    };

    // Helper function to format due date information
    const formatDueDate = (book: Book): string => {
        if (book.overdue) return `Overdue by ${book.days_overdue ?? '?'} days`;
        if (book.due_today) return 'Due Today';
        if (book.days_left !== null && book.days_left >= 0) return `Due in ${book.days_left} days`;
        // Fallback or if days_left is null/negative but not marked overdue for some reason
        return `Due: ${book.due_date ? new Date(book.due_date).toLocaleDateString() : 'N/A'}`;
    };

    // --- Render Logic ---

    if (isLoading) return <p>Loading borrowed books...</p>;
    if (error) return <p className="error-message">{error}</p>;
    // Check if currentUser exists before trying to display data
    if (!currentUser) return <p>Please log in to view borrowed books.</p>;

    // Check if data is loaded but empty
    if (!borrowedData || (Array.isArray(borrowedData) && borrowedData.length === 0)) {
        return (
            <div className="borrowed-books-list-container">
                <h2>{isPrivilegedUser ? "All Borrowed Books" : "My Borrowed Books"}</h2>
                <p>No borrowed books to display.</p>
            </div>
        );
    }

    // --- Render based on user type ---
    return (
        <div className="borrowed-books-list-container">
            <h2>{isPrivilegedUser ? "All Borrowed Books" : "My Borrowed Books"}</h2>
    
            {isPrivilegedUser && Array.isArray(borrowedData) ? (
                (borrowedData as BorrowedBooksGroup[]).map((userGroup) => (
                    <div key={userGroup.borrower_id} className="user-borrowed-books-group">
                        <h3>Borrowed by: {userGroup.borrower_name} (ID: {userGroup.borrower_id})</h3>
                        <div className="borrowed-books-grid">
                            {userGroup.books.map((book: Book) => (
                                <BookCard
                                    key={book.id}
                                    book={book}
                                    onBorrowReturn={handleReturnBook}
                                    currentUser={currentUser}
                                />
                            ))}
                        </div>
                    </div>
                ))
            ) : (
                <div className="borrowed-books-grid">
                    {(borrowedData as Book[]).map((book: Book) => (
                        <BookCard
                            key={book.id}
                            book={book}
                            onBorrowReturn={handleReturnBook}
                            currentUser={currentUser}
                        />
                    ))}
                </div>
            )}
        </div>
    );
    };

export default BorrowedBooksList;