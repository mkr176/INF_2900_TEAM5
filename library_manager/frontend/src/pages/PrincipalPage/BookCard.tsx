import React, { useState } from "react";
import { motion } from "framer-motion";
import "./PrincipalPage.css";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

// --- Interface Updates ---
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
  available: boolean;
  // image?: string | null; // Original field
  image_url?: string | null; // <<< ADD: Expect image URL >>>
  borrower: string | null;
  borrower_id: number | null;
  borrow_date: string | null;
  due_date: string | null;
  storage_location: string | null;
  publisher: string | null;
  publication_year: number | null;
  copy_number: number | null;
  added_by: string | null;
  added_by_id: number | null;
  days_left?: number | null;
  overdue?: boolean;
  days_overdue?: number | null;
  due_today?: boolean;
}

interface User {
  id: number;
  username: string;
  profile: {
    type: string;
    avatar_url?: string | null; // <<< CHANGE: Use avatar_url >>>
  } | null;
}


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
      if (currentUser && book.borrower_id === currentUser.id) {
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        return `Return Book (Due: ${dueDateStr})`;
      } else {
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        const borrowerName = book.borrower || "another user";
        return `Unavailable (Borrowed by ${borrowerName}, Due: ${dueDateStr})`;
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
    if ((e.target as HTMLElement).closest('button')) {
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