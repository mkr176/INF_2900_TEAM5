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
  category: string; // Code e.g., 'SF'
  category_display: string; // Display name e.g., 'Science Fiction'
  language: string;
  condition: string; // Code e.g., 'GD'
  condition_display: string; // Display name e.g., 'Good'
  available: boolean;
  image?: string | null; // Path relative to MEDIA_ROOT/STATIC_ROOT e.g., 'images/cover.jpg' or 'static/images/library_seal.jpg'
  borrower: string | null; // Username
  borrower_id: number | null;
  borrow_date: string | null; // ISO date string
  due_date: string | null; // ISO date string
  storage_location: string | null;
  publisher: string | null;
  publication_year: number | null;
  copy_number: number | null;
  added_by: string | null;
  added_by_id: number | null;
  // Derived fields (read-only from serializer)
  days_left?: number | null;
  overdue?: boolean;
  days_overdue?: number | null;
  due_today?: boolean;
}

// <<< ADDED: Constants/Helper for image path construction >>>
const STATIC_PATH_PREFIX = "/static/";
const DEFAULT_BOOK_IMAGE_PATH = "/static/images/library_seal.jpg"; // Full default path

const getFullImagePath = (relativePath: string | null | undefined): string => {
    if (relativePath && typeof relativePath === 'string' && relativePath.trim() !== '') {
        // If it already starts with /static/ or /media/ (if using media URLs), use it directly
        if (relativePath.startsWith('/static/') || relativePath.startsWith('/media/')) {
            return relativePath;
        }
        // Otherwise, assume it's relative to static root and needs the prefix
        // Handle cases like 'images/cover.jpg' or 'static/images/default.jpg'
        const cleanRelativePath = relativePath.startsWith('/') ? relativePath.substring(1) : relativePath;
        // Avoid double static prefix if default path is stored like 'static/images/...'
        if (cleanRelativePath.startsWith('static/')) {
             return '/' + cleanRelativePath; // Path is like /static/images/...
        }
        // Assume paths like 'images/cover.jpg' need the static prefix
        return STATIC_PATH_PREFIX + cleanRelativePath; // /static/images/cover.jpg
    }
    return DEFAULT_BOOK_IMAGE_PATH;
};


const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Get book ID from URL
  const navigate = useNavigate(); // Hook for navigation
  // <<< CHANGE: Get userType and currentUser from useAuth >>>
  const { getCSRFToken, userType, currentUser } = useAuth(); // Get CSRF token function and user type/info
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  const fetchBookDetails = useCallback(async () => { // Wrap in useCallback
    setLoading(true);
    setError(null);
    if (!id) {
        setError("Book ID is missing.");
        setLoading(false);
        return;
    }
    try {
      // <<< CHANGE: Use the new API endpoint >>>
      const response = await fetch(`/api/books/${id}/`, { credentials: 'include' }); // GET is default
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Book not found.");
        }
        // <<< CHANGE: Include status in error message >>>
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
  }, [id]); // Depend on id

  useEffect(() => {
      fetchBookDetails();
  }, [fetchBookDetails]); // Include fetchBookDetails in dependency array

  const handleBookUpdated = (updatedBook: Book) => {
    setBook(updatedBook); // Update local state with the updated book data
    setShowEditForm(false); // Close edit form
    // Optionally re-fetch if you want to be absolutely sure: fetchBookDetails();
  };

  const handleRemoveBook = async () => {
    if (!book) return;

    // <<< ADDED: Check permissions before allowing delete action >>>
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

        if (response.ok || response.status === 204) { // Status 204 No Content is OK for DELETE
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

  // <<< CHANGE: Use helper function for image path >>>
  const imagePath = getFullImagePath(book?.image);

  if (loading) {
    return <div className="book-detail-container"><p>Loading book details...</p></div>;
  }

  if (error) {
    return <div className="book-detail-container"><p className="error-message">{error}</p></div>;
  }

  if (!book) {
    // This case should be handled by the 404 check in fetchBookDetails or initial id check
    return <div className="book-detail-container"><p>Book not found or ID missing.</p></div>;
  }

  // Check if the current user is an Admin or Librarian
  const canEditOrDelete = userType === 'AD' || userType === 'LB';

  return (
    <div className="book-detail-container">
      <h1>{book.title}</h1>
      {/* <<< CHANGE: Use constructed imagePath >>> */}
      <img
        src={imagePath}
        alt={book.title}
        className="book-detail-image"
        onError={(e) => {
            console.warn(`Failed to load book image: ${imagePath}. Using default.`);
            (e.target as HTMLImageElement).src = DEFAULT_BOOK_IMAGE_PATH;
        }}
       />
      <div className="book-detail-info">
        <p><strong>Author:</strong> {book.author}</p>
        {/* <<< CHANGE: Use category_display >>> */}
        <p><strong>Category:</strong> {book.category_display || book.category}</p>
        <p><strong>Language:</strong> {book.language}</p>
        {/* <<< CHANGE: Use condition_display >>> */}
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
        {/* <<< ADDED: Display derived due date info if available >>> */}
        {!book.available && book.due_date && (
            <p><strong>Status:</strong>
                {book.overdue && <span className="overdue"> Overdue by {book.days_overdue ?? '?'} days</span>}
                {book.due_today && <span className="due-today"> Due Today</span>}
                {!book.overdue && !book.due_today && book.days_left !== null && <span> Due in {book.days_left} days</span>}
            </p>
        )}
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
