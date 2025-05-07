import React, { useState } from "react";
import { motion } from "framer-motion";
import "./PrincipalPage.css";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
// <<< ADD: Import shared types >>>
import { Book, User } from '../../types/models'; // Adjust path if needed



interface BookCardProps {
  book: Book;
  onBorrowReturn: (book: Book) => void;
  currentUser: User | null;
  onEditBook: (book: Book) => void;
  onRemoveBook: (bookId: number) => void;
}

// <<< ADD: Default book image URL (must match backend/serializer) >>>
const DEFAULT_BOOK_IMAGE_URL = "/static/images/library_seal.jpg";

const BookCard: React.FC<BookCardProps> = ({ book, onBorrowReturn, currentUser, onEditBook, onRemoveBook }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const { userType } = useAuth();
  const navigate = useNavigate();

  const getBorrowButtonText = (): string => {
    if (book.available) {
      return "Borrow Book";
    } else {
      // User is the borrower
      if (currentUser && book.borrower_id === currentUser.id) {
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        // `book.borrower` will be the username here due to serializer logic for the owner
        return `Return Book (Due: ${dueDateStr})`;
      } else {
        // Book is borrowed by someone else
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        // `book.borrower` will be username for Admin/Librarian, or "Checked Out" for regular user
        if (book.borrower === "Checked Out") {
           return `Unavailable (Checked Out, Due: ${dueDateStr})`;
        } else if (book.borrower) { // It's a username (for Admin/Librarian viewing others' checkouts)
           return `Unavailable (Borrowed by ${book.borrower}, Due: ${dueDateStr})`;
        } else { // Fallback, though !book.available implies a borrower or "Checked Out"
           return `Unavailable (Due: ${dueDateStr})`;
        }
      }
    }
  };

  const getBorrowButtonClassName = (): string => {
    if (!book.available && currentUser && book.borrower_id === currentUser.id) {
      return "button return-button";
    } else if (book.available) {
      return "button borrow-button available";
    } else {
      return "button borrow-button unavailable";
    }
  };

  const isBorrowButtonDisabled = (): boolean => {
    if (book.available) {
      return false;
    } else {
      return !(currentUser && book.borrower_id === currentUser.id);
    }
  };


  const handleEditClick = () => {
    onEditBook(book);
  };

  const handleRemoveClick = () => {
    onRemoveBook(book.id);
  };

  // <<< CHANGE: Use image_url from book data, fallback to default >>>
  const imagePath = book.image_url || DEFAULT_BOOK_IMAGE_URL;

  const handleCardClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Prevent navigation if a button inside the card was clicked
    if ((e.target as HTMLElement).closest('button')) {
      return;
    }
    // Prevent navigation if the click is on an interactive element on the back of the card (if any were added)
    // For now, let's assume only buttons are interactive. If other elements are added, extend this check.
    if ((e.target as HTMLElement).closest('.book-card-back button')) { // Example if back had buttons
      return;
    }
    navigate(`/books/${book.id}`);
  };


  return (
    <motion.div
      className="book-card-container"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {book.author === "Ine Arvola" && ( // Example condition
        <div className="recommended-badge">Recommended</div>
      )}

      <div
        className={`book-card ${isFlipped ? "flipped" : ""}`}
        onMouseEnter={() => setTimeout(() => setIsFlipped(true), 150)}
        onMouseLeave={() => setTimeout(() => setIsFlipped(false), 150)}
        onClick={handleCardClick}
        style={{ cursor: 'pointer' }}
      >
        <div className="book-card-inner">
          {/* Front Side */}
          <div className="book-card-front">
            {/* <<< CHANGE: Use imagePath (which is the full URL) >>> */}
            <img
                src={imagePath}
                alt={book.title}
                className="book-image"
                onError={(e) => {
                    console.warn(`Failed to load book image: ${imagePath}. Using default.`);
                    (e.target as HTMLImageElement).src = DEFAULT_BOOK_IMAGE_URL;
                }}
            />
            <h2 className="book-title">{book.title}</h2>
            <p className="book-author">{book.author}</p>
          </div>

          {/* Back Side (Details) */}
          <div className="book-card-back">
            <h3>{book.title}</h3>
            <p><strong>Author:</strong> {book.author}</p>
            <p><strong>Category:</strong> {book.category_display || book.category}</p>
            <p><strong>Condition:</strong> {book.condition_display || book.condition}</p>
            <p><strong>Language:</strong> {book.language}</p>
            <p><strong>ISBN:</strong> {book.isbn}</p>
            <p><strong>Publisher:</strong> {book.publisher || 'N/A'}</p>
            <p><strong>Year:</strong> {book.publication_year || 'N/A'}</p>
            <p><strong>Available:</strong> {book.available ? "Yes" : "No"}</p>
            {!book.available && book.due_date && (
              <p><strong>Due Date:</strong> {new Date(book.due_date).toLocaleDateString()}</p>
            )}
            {/* 
              Display borrower information on the back of the card.
              - If current user is Admin/Librarian, or if the current user is the borrower, show username.
              - If regular user views a book borrowed by someone else, `book.borrower` will be "Checked Out".
              - If book is available, `book.borrower` from serializer should be null.
            */}
            {!book.available && book.borrower && (
              <p><strong>Borrowed By:</strong> {book.borrower}</p>
            )}
          </div>
        </div>
      </div>

      {/* Book Actions */}
      <div className="book-actions">
        <button
          onClick={() => onBorrowReturn(book)}
          className={getBorrowButtonClassName()}
          disabled={isBorrowButtonDisabled()}
        >
          {getBorrowButtonText()}
        </button>
        {userType && (userType === "AD" || userType === "LB") && (
          <div className="admin-actions">
            <button
              className="button edit-button" onClick={handleEditClick}>Edit
            </button>
            <button
              className="button remove-button" onClick={handleRemoveClick}>Remove
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default BookCard;