import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom"; // Import useNavigate
import EditBookForm from "../../components/EditBookForm/EditBookForm";
import { useAuth } from "../../context/AuthContext"; // Import useAuth for CSRF token and user type
import "./BookDetailPage.css"; // Assuming you have styles

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
  available: boolean;
  image?: string | null;
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

const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Get book ID from URL
  const navigate = useNavigate(); // Hook for navigation
  const { getCSRFToken, userType } = useAuth(); // Get CSRF token function and user type
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  const fetchBookDetails = useCallback(async () => { // Wrap in useCallback
    setLoading(true);
    setError(null);
    try {
      // Use the new API endpoint
      const response = await fetch(`/api/books/${id}/`); // GET is default
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Book not found.");
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: Book = await response.json();
      setBook(data);
    } catch (err: any) {
      console.error("Error fetching book details:", err);
      setError(err.message || "Failed to load book details.");
    } finally {
      setLoading(false);
    }
  }, [id]); // Depend on id

  useEffect(() => {
    if (id) {
      fetchBookDetails();
    } else {
      setError("Book ID is missing.");
      setLoading(false);
    }
  }, [id, fetchBookDetails]); // Include fetchBookDetails in dependency array

  const handleBookUpdated = (updatedBook: Book) => {
    setBook(updatedBook); // Update local state with the updated book data
    setShowEditForm(false); // Close edit form
    // Optionally re-fetch if you want to be absolutely sure: fetchBookDetails();
  };

  const handleRemoveBook = async () => {
    if (!book) return;

    if (window.confirm(`Are you sure you want to remove "${book.title}"? This action cannot be undone.`)) {
      const csrfToken = await getCSRFToken();
      if (!csrfToken) {
        alert("Error: Could not verify security token. Please refresh and try again.");
        return;
      }

      setLoading(true); // Indicate loading state
      try {
        // Use the new API endpoint and DELETE method
        const response = await fetch(`/api/books/${book.id}/`, {
          method: "DELETE",
          headers: {
            "X-CSRFToken": csrfToken, // Include CSRF token
          },
          credentials: "include", // Include cookies if needed
        });

        if (response.ok) { // Status 204 No Content is OK
          alert(`Book "${book.title}" removed successfully.`);
          navigate("/principal"); // Navigate back to the main list page
        } else {
          // Try to get error message from response
          let errorMsg = `Failed to remove book. Status: ${response.status}`;
          try {
            const errData = await response.json();
            errorMsg = errData.detail || JSON.stringify(errData) || errorMsg;
          } catch (e) { /* Ignore if response not JSON */ }
          throw new Error(errorMsg);
        }
      } catch (err: any) {
        console.error("Error removing book:", err);
        alert(`Error removing book: ${err.message}`);
        setLoading(false); // Stop loading on error
      }
      // No finally block needed for setLoading here, as navigation happens on success
    }
  };

  // Construct image path using /static/ prefix
  const imagePath = book?.image ? `${book.image}` : '/static/images/library_seal.jpg';

  if (loading) {
    return <div className="book-detail-container"><p>Loading book details...</p></div>;
  }

  if (error) {
    return <div className="book-detail-container"><p className="error-message">{error}</p></div>;
  }

  if (!book) {
    // This case should be handled by the 404 check in fetchBookDetails
    return <div className="book-detail-container"><p>Book not found.</p></div>;
  }

  // Check if the current user is an Admin or Librarian
  const canEditOrDelete = userType === 'AD' || userType === 'LB';

  return (
    <div className="book-detail-container">
      <h1>{book.title}</h1>
      <img src={imagePath} alt={book.title} className="book-detail-image" />
      <div className="book-detail-info">
        <p><strong>Author:</strong> {book.author}</p>
        <p><strong>Category:</strong> {book.category_display}</p>
        <p><strong>Language:</strong> {book.language}</p>
        <p><strong>Condition:</strong> {book.condition_display}</p>
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
      </div>

      {/* Edit and Delete Buttons (Admin/Librarian only) */}
      {canEditOrDelete && (
        <div className="admin-actions-detail">
          <button onClick={() => setShowEditForm(true)} disabled={showEditForm || loading} className="button edit-button">Edit Book</button>
          <button onClick={handleRemoveBook} disabled={loading} className="button remove-button">
            {loading ? 'Removing...' : 'Remove Book'}
          </button>
        </div>
      )}


      {/* Edit Form Modal or Section */}
      {showEditForm && canEditOrDelete && (
        <div className="edit-form-modal"> {/* Add styling for modal/overlay */}
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
