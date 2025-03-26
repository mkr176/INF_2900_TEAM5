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


    useEffect(() => {
        // Determine if special view should be active based on user type
        const isLibrarianOrAdmin = currentUser && (currentUser.type === "AD" || currentUser.type === "LB");
        setSpecialViewActive(isLibrarianOrAdmin); // Set specialViewActive based on user role

        fetch('/api/borrowed_books/')
            .then(response => response.json())
            .then(data => {
                console.log("Full API response data:", data); // Log the entire response
                console.log("Borrowed books by user data:", data.borrowed_books_by_user); // Log specifically borrowed_books_by_user
                console.dir(data.borrowed_books_by_user, {depth: null}); // Log with object inspector to see full structure
                setBorrowedBooksByUser(data.borrowed_books_by_user);
            })
            .catch(error => console.error('Error fetching borrowed books:', error));
     }, [currentUser]);


    return (
        <div className="borrowed-books-list-container">
            <h2>Borrowed Books</h2>

            {/* Special View Button for Librarians and Admins */}
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