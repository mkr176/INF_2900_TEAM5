import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "./PrincipalPage.css"; // Make sure to keep the import for CSS

interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  category: string;
  language: string;
  user_id: number;
  condition: string;
  available: boolean;
  image?: string;
  borrower_id: number | null;
  due_date: string;
  publisher: string;
  publication_year: number;
}
interface People {
  id: number;
  username: string;
  email: string;
  type: string;
  numberofbooks: number;
  password?: string;
}

const BookCard: React.FC<{ book: Book, onBorrow: () => void }> = ({ book, onBorrow }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [currentUser, setCurrentUser] = useState<People | null>(null); // Add currentUser state

  useEffect(() => {
    // Fetch current user data on component mount
    fetch("/api/current_user/")
      .then((response) => response.json())
      .then((data) => setCurrentUser(data))
      .catch((error) => console.error("Error fetching current user:", error));
  }, []);


  const getBorrowButtonText = (): string => { // Function to determine button text
    if (book.available) {
      return "Borrow Book";
    } else {
      if (currentUser && book.borrower_id === currentUser.id) { // Check if borrowed by current user
        const dueDate = new Date(book.due_date).toLocaleDateString();
        return `Return Book - due date: ${dueDate}`; // Return book text with due date
      } else {
        const dueDate = new Date(book.due_date).toLocaleDateString();
        return `Unavailable until ${dueDate}`;
      }
    }
  };

  const getBorrowButtonClassName = (): string => { // Function to determine button style
    if (!book.available && currentUser && book.borrower_id === currentUser.id) {
      return "button return-button"; // Apply return-button class for yellow style
    } else {
      return `button borrow-button ${book.available ? "available" : "unavailable"}`; // Default classes
    }
  };


  return (
    <motion.div
      className="book-card-container"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Flipping Book Card */}
      <div
        className={`book-card ${isFlipped ? "flipped" : ""}`}
        onMouseEnter={() => setTimeout(() => setIsFlipped(true), 150)}
        onMouseLeave={() => setTimeout(() => setIsFlipped(false), 150)}
      >
        <div className="book-card-inner">
          {/* Front Side */}
          <div className="book-card-front">
            <img src={book.image} alt={book.title} className="book-image" />
            <h2 className="book-title">{book.title}</h2>
          </div>

          {/* Back Side (Details) */}
          <div className="book-card-back">
            <h3>{book.title}</h3>
            <p><strong>Author:</strong> {book.author}</p>
            <p><strong>Category:</strong> {book.category}</p>
            <p><strong>Condition:</strong> {book.condition}</p>
            <p><strong>Language:</strong> {book.language}</p>
            <p><strong>ISBN:</strong> {book.isbn}</p>
            <p><strong>Publisher:</strong> {book.publisher}</p>
            <p><strong>Year:</strong> {book.publication_year}</p>
            <p><strong>Available:</strong> {book.available ? "Yes" : "No"}</p>
          </div>
        </div>
      </div>

      {/* Borrow Button Always Below */}
      <div className="book-actions">
        <button
          onClick={onBorrow}
          className={getBorrowButtonClassName()} // Use function to get class names
          >
          {getBorrowButtonText()} {/* Use function to get button text */}
        </button>
      </div>
    </motion.div>
  );
};

export default BookCard;