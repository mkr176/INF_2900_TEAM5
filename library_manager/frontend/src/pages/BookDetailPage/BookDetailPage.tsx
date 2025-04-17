import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import EditBookForm from "../../components/EditBookForm/EditBookForm";
import { useAuth } from "../../context/AuthContext";
import "./BookDetailPage.css";

// Updated Book interface
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

// <<< REMOVE: Static path prefix and helper function >>>
// const STATIC_PATH_PREFIX = "/static/";
// const getFullImagePath = (...) => { ... };

// <<< ADD: Default book image URL (must match backend/serializer) >>>
const DEFAULT_BOOK_IMAGE_URL = "/static/images/library_seal.jpg";


const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getCSRFToken, userType, currentUser } = useAuth();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  const fetchBookDetails = useCallback(async () => {
    setLoading(true);
    setError(null);
    if (!id) {
        setError("Book ID is missing.");
        setLoading(false);
        return;
    }
    try {
      const response = await fetch(`/api/books/${id}/`, { credentials: 'include' });
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Book not found.");
        }
        const errorText = await response.text();
        throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
      }
      const data: Book = await response.json();
      setBook(data);
    } catch (err: any) {
      console.error("Error fetching book details:", err);
      setError(err.message || "Failed to load book details.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
      fetchBookDetails();
  }, [fetchBookDetails]);

  const handleBookUpdated = (updatedBook: Book) => {
    setBook(updatedBook);
    setShowEditForm(false);
  };

  const handleRemoveBook = async () => {
    if (!book) return;
    if (!(userType === 'AD' || userType === 'LB')) {
        alert("You do not have permission to remove books.");
        return;
    }

    if (window.confirm(`Are you sure you want to remove "${book.title}"? This action cannot be undone.`)) {
      const csrfToken = await getCSRFToken();
      if (!csrfToken) {
        alert("Error: Could not verify security token. Please refresh and try again.");
        return;
      }

      setLoading(true);
      try {
        const response = await fetch(`/api/books/${book.id}/`, {
          method: "DELETE",
          headers: {
            "X-CSRFToken": csrfToken,
          },
          credentials: "include",
        });

        if (response.ok || response.status === 204) {
          alert(`Book "${book.title}" removed successfully.`);
          navigate("/principal");
        } else {
          let errorMsg = `Failed to remove book. Status: ${response.status}`;
          try {
            const errData = await response.json();
            errorMsg = errData.detail || JSON.stringify(errData) || errorMsg;
          } catch (e) { /* Ignore */ }
          throw new Error(errorMsg);
        }
      } catch (err: any) {
        console.error("Error removing book:", err);
        alert(`Error removing book: ${err.message}`);
        setLoading(false);
      }
    }
  };

  // <<< CHANGE: Use image_url from book data, fallback to default >>>
  const imagePath = book?.image_url || DEFAULT_BOOK_IMAGE_URL;

  if (loading) {
    return <div className="book-detail-container"><p>Loading book details...</p></div>;
  }
  if (error) {
    return <div className="book-detail-container"><p className="error-message">{error}</p></div>;
  }
  if (!book) {
    return <div className="book-detail-container"><p>Book not found or ID missing.</p></div>;
  }

  const canEditOrDelete = userType === 'AD' || userType === 'LB';

  return (
    <div className="book-detail-container">
      <h1>{book.title}</h1>
      {/* <<< CHANGE: Use imagePath (full URL) >>> */}
      <img
        src={imagePath}
        alt={book.title}
        className="book-detail-image"
        onError={(e) => {
            console.warn(`Failed to load book image: ${imagePath}. Using default.`);
            // <<< CHANGE: Fallback to default URL >>>
            (e.target as HTMLImageElement).src = DEFAULT_BOOK_IMAGE_URL;
        }}
       />
      <div className="book-detail-info">
        <p><strong>Author:</strong> {book.author}</p>
        <p><strong>Category:</strong> {book.category_display || book.category}</p>
        <p><strong>Language:</strong> {book.language}</p>
        <p><strong>Condition:</strong> {book.condition_display || book.condition}</p>
        <p><strong>ISBN:</strong> {book.isbn}</p>
        <p><strong>Publisher:</strong> {book.publisher || 'N/A'}</p>
        <p><strong>Year:</strong> {book.publication_year || 'N/A'}</p>
        <p><strong>Storage Location:</strong> {book.storage_location || 'N/A'}</p>
        <p>
          <strong>Availability:</strong>{" "}
          <span className={book.available ? "available-text" : "unavailable-text"}>
            {book.available
              ? "Available"
              : `Checked out by ${book.borrower || 'N/A'}${book.due_date ? ` until ${new Date(book.due_date).toLocaleDateString()}` : ''}`
            }
          </span>
        </p>
        {book.added_by && <p><strong>Added By:</strong> {book.added_by}</p>}
        {!book.available && book.due_date && (
            <p><strong>Status:</strong>
                {book.overdue && <span className="overdue"> Overdue by {book.days_overdue ?? '?'} days</span>}
                {book.due_today && <span className="due-today"> Due Today</span>}
                {!book.overdue && !book.due_today && book.days_left !== null && <span> Due in {book.days_left} days</span>}
            </p>
        )}
      </div>

      {canEditOrDelete && (
        <div className="admin-actions-detail">
          <button onClick={() => setShowEditForm(true)} disabled={showEditForm || loading} className="button edit-button">Edit Book</button>
          <button onClick={handleRemoveBook} disabled={loading} className="button remove-button">
            {loading ? 'Removing...' : 'Remove Book'}
          </button>
        </div>
      )}

      {showEditForm && canEditOrDelete && (
        <div className="edit-form-modal">
          <EditBookForm
            book={book}
            onBookUpdated={handleBookUpdated}
            onCancel={() => setShowEditForm(false)}
          />
        </div>
      )}
    </div>
  );
};

export default BookDetailPage;