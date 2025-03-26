// library_manager\frontend\src\components\BorrowedBooksList\BorrowedBooksList.tsx
import React, { useState, useEffect } from 'react';
import "./BorrowedBooksList.css"; // ✅ Create and import CSS file

interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string;
    language: string;
    condition: string;
    image?: string;
    due_date: string;
    borrower_id: number | null;
    days_left: number;
    overdue: boolean;
    days_overdue: number;
    due_today: boolean;
}

interface People {
    id: number;
    username: string;
    type: string;
}

interface BorrowedBooksListProps {
    currentUser: People | null;
}


const BorrowedBooksList: React.FC<BorrowedBooksListProps> = ({ currentUser }) => {
    const [borrowedBooksByUser, setBorrowedBooksByUser] = useState<any[] | undefined>(undefined); // ✅ Initialize as undefined and allow undefined type
    const [specialViewActive, setSpecialViewActive] = useState(false); // State for special view, default to false

    const fetchBorrowedBooks = async () => {
        try {
            const response = await fetch('/api/borrowed_books/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Borrowed books data fetched:", data.borrowed_books_by_user);
            setBorrowedBooksByUser(data.borrowed_books_by_user);
        } catch (error) {
            console.error('Error fetching borrowed books:', error);
        }
    };


    useEffect(() => {
        // Determine if special view should be active based on user type
        const isLibrarianOrAdmin = currentUser && (currentUser.type === "AD" || currentUser.type === "LB");
        setSpecialViewActive(isLibrarianOrAdmin); // Set specialViewActive based on user role
        fetchBorrowedBooks();
     }, [currentUser]);

    const handleReturnBook = async (bookId: number, userId: number | undefined) => {
        if (!userId) {
            alert("User ID is not available.");
            return;
        }
        try {
            const response = await fetch('/api/borrow_book/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            });

            if (!response.ok) {
                const errorData = await response.json(); // Try to parse error message from backend
                throw new Error(errorData.error || `Failed to return book: HTTP status ${response.status}`);
            }

            alert('Book returned successfully!');
            fetchBorrowedBooks(); // Refresh the list after returning

        } catch (error: any) { // error is of type 'any' to access 'message' property
            console.error("Error returning book:", error);
            alert(`Error returning book: ${error.message}`); // Display error message from backend or default message
        }
    };


    return (
        <div className="borrowed-books-list-container">
            <h2>Borrowed Books</h2>

            {/* Special View Button for Librarians and Admins -  No longer needed here */}

            {borrowedBooksByUser === undefined ? ( // ✅ Show loading state
                <p>Loading borrowed books...</p>
            ) : borrowedBooksByUser && borrowedBooksByUser.length > 0 ? ( // ✅ Check if borrowedBooksByUser is truthy and is an array with length
                borrowedBooksByUser.map((userGroup, index) => (
                <div key={index} className="user-borrowed-books-group">
                    <h3>{specialViewActive ? `${userGroup.borrower_name}` : 'My Borrowed Books'}</h3> {/* Conditional heading */}
                    <ul className="borrowed-books-ul">
                        {userGroup.books.map((book: Book) => (
                            <li key={book.id} className={`borrowed-book-item ${book.due_today ? 'due-today' : ''} ${book.overdue ? 'overdue' : ''}`}>
                                <span className="book-title">{book.title}</span> by <span className="book-author">{book.author}</span>
                                {specialViewActive && ( // ✅ Display days left/overdue only in special view
                                    <>
                                        {book.overdue ?
                                            <span className="book-overdue"> - Overdue by {book.days_overdue} days</span> :
                                            <span className="book-due-date"> - {book.due_today ? 'Due Today' : `Due in ${book.days_left} days`}</span>
                                        }
                                    </>
                                )}
                                {!specialViewActive && ( // ✅ Display due date for normal user view
                                    <span className="book-due-date"> - Due Date: {new Date(book.due_date).toLocaleDateString()}</span>
                                )}
                                {/* ✅ Return Button */}
                                <button
                                    className="button button-return-book"
                                    onClick={() => handleReturnBook(book.id, book.borrower_id)}
                                >
                                    Return
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
                ))
            ) : ( // ✅ Handle case when there are no borrowed books
                <p>No borrowed books to display.</p>
            )}
        </div>
    );
};

export default BorrowedBooksList;