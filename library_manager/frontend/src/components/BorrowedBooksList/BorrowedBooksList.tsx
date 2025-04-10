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
    const [borrowedBooksByUser, setBorrowedBooksByUser] = useState<any[] | undefined>(undefined);
    const [specialViewActive, setSpecialViewActive] = useState(false);
    const [selectedConditions, setSelectedConditions] = useState<{ [key: number]: string }>({}); // Estado para almacenar las condiciones seleccionadas

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
        const isLibrarianOrAdmin = currentUser && (currentUser.type === "AD" || currentUser.type === "LB");
        setSpecialViewActive(isLibrarianOrAdmin);
        fetchBorrowedBooks();
    }, [currentUser]);

    const handleReturnBook = async (bookId: number, userId: number | undefined, condition: string) => {
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
                body: JSON.stringify({ book_id: bookId, user_id: userId, condition: condition }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Failed to return book: HTTP status ${response.status}`);
            }

            alert('Book returned successfully!');
            fetchBorrowedBooks(); // Refresh the list after returning
        } catch (error: any) {
            console.error("Error returning book:", error);
            alert(`Error returning book: ${error.message}`);
        }
    };

    const handleConditionChange = (bookId: number, newCondition: string) => {
        setSelectedConditions((prev) => ({
            ...prev,
            [bookId]: newCondition,
        }));
    };

    return (
        <div className="borrowed-books-list-container">
            <h2>Borrowed Books</h2>
            {borrowedBooksByUser === undefined ? (
                <p>Loading borrowed books...</p>
            ) : borrowedBooksByUser && borrowedBooksByUser.length > 0 ? (
                borrowedBooksByUser.map((userGroup, index) => (
                    <div key={index} className="user-borrowed-books-group">
                        <h3>{specialViewActive ? `${userGroup.borrower_name}` : 'My Borrowed Books'}</h3>
                        <ul className="borrowed-books-ul">
                            {userGroup.books.map((book: Book) => (
                                <li
                                    key={book.id}
                                    className={`borrowed-book-item ${book.due_today ? 'due-today' : ''} ${book.overdue ? 'overdue' : ''}`}
                                >
                                    <span className="book-title">{book.title}</span> by <span className="book-author">{book.author}</span>
                                    {specialViewActive && (
                                        <>
                                            {book.overdue ? (
                                                <span className="book-overdue"> - Overdue by {book.days_overdue} days</span>
                                            ) : (
                                                <span className="book-due-date">
                                                    - {book.due_today ? 'Due Today' : `Due in ${book.days_left} days`}
                                                </span>
                                            )}
                                        </>
                                    )}
                                    {!specialViewActive && (
                                        <span className="book-due-date"> - Due Date: {new Date(book.due_date).toLocaleDateString()}</span>
                                    )}
                                    {/* Dropdown to change book status */}
                                    <div className="book-status-dropdown">
                                        <select
                                            id={`status-${book.id}`}
                                            defaultValue={book.condition}
                                            onChange={(e) => handleConditionChange(book.id, e.target.value)}
                                        >
                                            <option value="NW">New</option>
                                            <option value="GD">Good</option>
                                            <option value="FR">Fair</option>
                                            <option value="PO">Poor</option>
                                        </select>
                                    </div>
                                    {/* Return Button */}
                                    <button
                                        className="button button-return-book"
                                        onClick={() =>
                                            handleReturnBook(book.id, book.borrower_id, selectedConditions[book.id] || book.condition)
                                        }
                                    >
                                        Return
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))
            ) : (
                <p>No borrowed books to display.</p>
            )}
        </div>
    );
};

export default BorrowedBooksList;