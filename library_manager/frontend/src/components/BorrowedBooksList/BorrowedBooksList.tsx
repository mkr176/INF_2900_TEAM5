// library_manager\frontend\src\components\BorrowedBooksList\BorrowedBooksList.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext'; // Import useAuth
import "./BorrowedBooksList.css";

// --- Interface Updates ---

// Updated Book interface based on BookSerializer
interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string;
    category_display: string;
    language: string;
    condition: string;
    condition_display: string;
    available: boolean; // Should always be false here
    image?: string | null;
    borrower: string | null; // Username of the borrower
    borrower_id: number | null; // ID of the borrower
    borrow_date: string | null;
    due_date: string | null;
    // Derived fields from serializer
    days_left: number | null;
    overdue: boolean;
    days_overdue: number | null;
    due_today: boolean;
    // Other fields if needed for display
    storage_location?: string | null;
    publisher?: string | null;
    publication_year?: number | null;
    copy_number?: number | null;
    added_by?: string | null;
    added_by_id?: number | null;
}

// Interface for the structure when grouped by user (Admin/Librarian view)
interface BorrowedBooksGroup {
    borrower_id: number;
    borrower_name: string;
    books: Book[];
}

// Updated People interface (User) from AuthContext
interface User {
    id: number;
    username: string;
    profile: {
        type: string; // 'AD', 'US', 'LB'
    } | null;
}

interface BorrowedBooksListProps {
    // No props needed as context is used
}

const BorrowedBooksList: React.FC<BorrowedBooksListProps> = () => {
    const { currentUser, getCSRFToken } = useAuth(); // Get user and CSRF function from context
    const [borrowedData, setBorrowedData] = useState<Book[] | BorrowedBooksGroup[] | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Determine if the current user is Admin or Librarian
    const isPrivilegedUser = currentUser?.profile?.type === "AD" || currentUser?.profile?.type === "LB";

    const fetchBorrowedBooks = useCallback(async () => {
        if (!currentUser) return; // Don't fetch if user isn't loaded

        setIsLoading(true);
        setError(null);
        try {
            // Use the new endpoint
            const response = await fetch('/api/books/borrowed/', { credentials: 'include' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Borrowed books data fetched:", data);

            // Set data based on user type
            if (isPrivilegedUser) {
                // Ensure the structure matches BorrowedBooksGroup[]
                const groupedData: BorrowedBooksGroup[] = data.borrowed_books_by_user || [];
                setBorrowedData(groupedData);
            } else {
                // Ensure the structure matches Book[]
                const flatData: Book[] = data.my_borrowed_books || [];
                setBorrowedData(flatData);
            }
        } catch (err: any) {
            console.error('Error fetching borrowed books:', err);
            setError(err.message || 'Failed to load borrowed books.');
            setBorrowedData(null);
        } finally {
            setIsLoading(false);
        }
    }, [currentUser, isPrivilegedUser]); // Depend on currentUser and derived isPrivilegedUser

    useEffect(() => {
        fetchBorrowedBooks();
    }, [fetchBorrowedBooks]); // Run fetch when the function reference changes

    const handleReturnBook = async (bookId: number) => {
        // Confirmation dialog
        if (!window.confirm("Are you sure you want to return this book?")) {
            return;
        }

        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Error: Could not verify security token. Please refresh and try again.");
            return;
        }

        try {
            // Use the new return endpoint
            const response = await fetch(`/api/books/${bookId}/return/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Include CSRF token
                },
                credentials: 'include',
                // No body needed for this specific return endpoint based on views.py
            });

            if (!response.ok) {
                const errorData = await response.json(); // Try to parse error message
                throw new Error(errorData.error || `Failed to return book: HTTP status ${response.status}`);
            }

            const result = await response.json();
            alert(result.message || 'Book returned successfully!');
            fetchBorrowedBooks(); // Refresh the list after returning

        } catch (error: any) {
            console.error("Error returning book:", error);
            alert(`Error returning book: ${error.message}`);
        }
    };

    // Helper to format due date string
    const formatDueDate = (book: Book): string => {
        if (book.overdue) {
            return `Overdue by ${book.days_overdue ?? '?'} days`;
        }
        if (book.due_today) {
            return 'Due Today';
        }
        if (book.days_left !== null) {
            return `Due in ${book.days_left} days`;
        }
        return `Due: ${book.due_date ? new Date(book.due_date).toLocaleDateString() : 'N/A'}`;
    };


    if (isLoading) {
        return <p>Loading borrowed books...</p>;
    }

    if (error) {
        return <p className="error-message">{error}</p>;
    }

    if (!borrowedData || (Array.isArray(borrowedData) && borrowedData.length === 0)) {
        return <p>No borrowed books to display.</p>;
    }

    return (
        <div className="borrowed-books-list-container">
            <h2>Borrowed Books</h2>

            {/* Render based on user type */}
            {isPrivilegedUser && Array.isArray(borrowedData) ? (
                // Admin/Librarian View: Grouped by user
                (borrowedData as BorrowedBooksGroup[]).map((userGroup) => (
                    <div key={userGroup.borrower_id} className="user-borrowed-books-group">
                        <h3>{userGroup.borrower_name} (ID: {userGroup.borrower_id})</h3>
                        {userGroup.books.length > 0 ? (
                            <ul className="borrowed-books-ul">
                                {userGroup.books.map((book: Book) => (
                                    <li key={book.id} className={`borrowed-book-item ${book.due_today ? 'due-today' : ''} ${book.overdue ? 'overdue' : ''}`}>
                                        <div>
                                            <span className="book-title">{book.title}</span> by <span className="book-author">{book.author}</span>
                                            <span className={`book-due-status ${book.overdue ? 'book-overdue' : ''}`}> - {formatDueDate(book)}</span>
                                            (<span className="book-due-date-explicit">Due: {book.due_date ? new Date(book.due_date).toLocaleDateString() : 'N/A'}</span>)
                                        </div>
                                        {/* Admin/Librarian can return any book */}
                                        <button
                                            className="button button-return-book"
                                            onClick={() => handleReturnBook(book.id)}
                                        >
                                            Return
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p>No books currently borrowed by this user.</p>
                        )}
                    </div>
                ))
            ) : !isPrivilegedUser && Array.isArray(borrowedData) ? (
                // Regular User View: Flat list
                <div className="user-borrowed-books-group">
                    <h3>My Borrowed Books</h3>
                    {(borrowedData as Book[]).length > 0 ? (
                        <ul className="borrowed-books-ul">
                            {(borrowedData as Book[]).map((book: Book) => (
                                <li key={book.id} className={`borrowed-book-item ${book.due_today ? 'due-today' : ''} ${book.overdue ? 'overdue' : ''}`}>
                                    <div>
                                        <span className="book-title">{book.title}</span> by <span className="book-author">{book.author}</span>
                                        <span className={`book-due-status ${book.overdue ? 'book-overdue' : ''}`}> - {formatDueDate(book)}</span>
                                        (<span className="book-due-date-explicit">Due: {book.due_date ? new Date(book.due_date).toLocaleDateString() : 'N/A'}</span>)
                                    </div>
                                    {/* User can only return their own books */}
                                    <button
                                        className="button button-return-book"
                                        onClick={() => handleReturnBook(book.id)}
                                    >
                                        Return
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>You have not borrowed any books.</p>
                    )}
                </div>
            ) : (
                <p>No borrowed books data available.</p> // Fallback
            )}
        </div>
    );
};

export default BorrowedBooksList;
