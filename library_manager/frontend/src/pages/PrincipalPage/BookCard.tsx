import React, { useState } from "react"; // Removed useEffect as it's not used
import { motion } from "framer-motion";
import "./PrincipalPage.css"; // Make sure to keep the import for CSS
import { useAuth } from "../../context/AuthContext"; // Import useAuth to get CSRF token and user info
import { useNavigate } from "react-router-dom"; // Import useNavigate

// --- Interface Updates ---

// Updated Book interface based on BookSerializer
interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  category: string; // Keep the code (e.g., 'CK')
  category_display: string; // Add display name (e.g., 'Cooking')
  language: string;
  condition: string; // Keep the code (e.g., 'GD')
  condition_display: string; // Add display name (e.g., 'Good')
  available: boolean;
  image?: string | null; // Image path from backend (can be null)
  borrower: string | null; // Username of the borrower (read-only)
  borrower_id: number | null; // ID of the borrower (read-only)
  borrow_date: string | null; // Read-only
  due_date: string | null; // Read-only
  storage_location: string | null;
  publisher: string | null;
  publication_year: number | null;
  copy_number: number | null; // Changed to number? Check serializer/model
  added_by: string | null; // Username of adder (read-only)
  added_by_id: number | null; // ID of adder (read-only)
  // Derived fields (read-only)
  days_left?: number | null;
  overdue?: boolean;
  days_overdue?: number | null;
  due_today?: boolean;
}

// Updated People interface based on UserSerializer (simplified for context)
interface User {
  id: number;
  username: string;
  profile: {
    type: string; // 'AD', 'US', 'LB'
    avatar?: string | null;
  } | null;
}


interface BookCardProps {
  book: Book;
  onBorrowReturn: (book: Book) => void; // Renamed for clarity
  currentUser: User | null; // Use updated User interface
  onEditBook: (book: Book) => void;
  onRemoveBook: (bookId: number) => void;
}

// Removed categoryMap and conditionMap as display values come from serializer

const BookCard: React.FC<BookCardProps> = ({ book, onBorrowReturn, currentUser, onEditBook, onRemoveBook }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const { userType } = useAuth(); // Get userType from context for conditional rendering
  const navigate = useNavigate(); // Hook for navigation

  const getBorrowButtonText = (): string => {
    if (book.available) {
      return "Borrow Book";
    } else {
      // Check if the current user is the borrower
      if (currentUser && book.borrower_id === currentUser.id) {
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        return `Return Book (Due: ${dueDateStr})`; // Changed text
      } else {
        // If borrowed by someone else
        const dueDateStr = book.due_date ? new Date(book.due_date).toLocaleDateString() : "N/A";
        const borrowerName = book.borrower || "another user";
        return `Unavailable (Borrowed by ${borrowerName}, Due: ${dueDateStr})`;
      }
    }
  };

  const getBorrowButtonClassName = (): string => {
    if (!book.available && currentUser && book.borrower_id === currentUser.id) {
      // Borrowed by current user -> Return button style
      return "button return-button"; // Use a specific class for return
    } else if (book.available) {
      // Available -> Borrow button style
      return "button borrow-button available";
    } else {
      // Unavailable and not borrowed by current user -> Disabled style
      return "button borrow-button unavailable";
    }
  };

  // Check if the borrow/return button should be disabled
  const isBorrowButtonDisabled = (): boolean => {
    if (book.available) {
      return false; // Can always attempt to borrow if available
    } else {
      // If unavailable, only enable if the current user is the borrower
      return !(currentUser && book.borrower_id === currentUser.id);
    }
  };


  const handleEditClick = () => {
    onEditBook(book);
  };

  const handleRemoveClick = () => {
    // Confirmation is handled in PrincipalPage
    onRemoveBook(book.id);
  };

  // Construct image path - assuming backend provides a usable path
  // (either relative to static root like 'images/covers/book.jpg' or absolute like '/static/images/covers/book.jpg')
  // <<< FIX: Remove the manual /static/ prefix >>>
  const imagePath = book.image ? `${book.image}` : '/static/images/library_seal.jpg'; // Default image if book.image is null/empty

  // Function to navigate to detail page
  const handleCardClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Prevent navigation if clicking on buttons inside the card
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
      {/* Recommended Badge - Keep existing logic or adapt if needed */}
      {book.author === "Ine Arvola" && (
        <div className="recommended-badge">Recommended</div>
      )}

      {/* Flipping Book Card */}
      <div
        className={`book-card ${isFlipped ? "flipped" : ""}`}
        onMouseEnter={() => setTimeout(() => setIsFlipped(true), 150)}
        onMouseLeave={() => setTimeout(() => setIsFlipped(false), 150)}
        onClick={handleCardClick} // Add onClick handler here
        style={{ cursor: 'pointer' }} // Indicate it's clickable
      >
        <div className="book-card-inner">
          {/* Front Side */}
          <div className="book-card-front">
            {/* Use updated imagePath */}
            <img src={imagePath} alt={book.title} className="book-image" />
            <h2 className="book-title">{book.title}</h2>
            <p className="book-author">{book.author}</p>
          </div>

          {/* Back Side (Details) */}
          <div className="book-card-back">
            <h3>{book.title}</h3>
            <p><strong>Author:</strong> {book.author}</p>
            {/* Use display values from serializer */}
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
        {/* Borrow/Return Button */}
        <button
          onClick={() => onBorrowReturn(book)} // Use renamed prop
          className={getBorrowButtonClassName()}
          disabled={isBorrowButtonDisabled()} // Disable based on logic
        >
          {getBorrowButtonText()}
        </button>
        {/* Edit/Remove Buttons for Admin/Librarian */}
        {userType && (userType === "AD" || userType === "LB") && (
          <div className="admin-actions"> {/* Optional: wrap in a div */}
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
