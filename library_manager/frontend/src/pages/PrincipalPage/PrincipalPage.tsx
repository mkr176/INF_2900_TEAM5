import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./PrincipalPage.css";
import AddBookForm from "../../components/AddBookForm/AddBookForm";
import EditBookForm from "../../components/EditBookForm/EditBookForm";
import BookCard from "./BookCard";
import BorrowedBooksList from "../../components/BorrowedBooksList/BorrowedBooksList";
import { useAuth } from "../../context/AuthContext"; // Import useAuth

// --- Interface Updates ---

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

// Updated People interface (User) from AuthContext
interface User {
    id: number;
    username: string;
    profile: {
        type: string; // 'AD', 'US', 'LB'
        avatar?: string | null;
    } | null;
}

const BookDisplayPage: React.FC = () => {
  const { currentUser, userType, getCSRFToken } = useAuth(); // Use AuthContext
  const [bookList, setBookList] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddBookForm, setShowAddBookForm] = useState(false);
  const [showEditBookForm, setShowEditBookForm] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [selectedCategory, setSelectedCategory] = useState(''); // For category filter
  const [showBorrowedBooks, setShowBorrowedBooks] = useState(false);

  // Define bookCategories (same as Add/Edit forms)
  const bookCategories = [
    { value: '', label: 'All Categories' }, { value: 'CK', label: 'Cooking' },
    { value: 'CR', label: 'Crime' }, { value: 'MY', label: 'Mystery' },
    { value: 'SF', label: 'Science Fiction' }, { value: 'FAN', label: 'Fantasy' },
    { value: 'HIS', label: 'History' }, { value: 'ROM', label: 'Romance' },
    { value: 'TXT', label: 'Textbook' },
  ];

  // Fetch books function
  const fetchBooks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    // Construct fetch URL with category filter if selected
    let fetchUrl = '/api/books/'; // Use the new endpoint
    const queryParams = new URLSearchParams();
    if (selectedCategory) {
        queryParams.append('category', selectedCategory);
    }
    // Add other filters like search here if moving search to backend
    // if (searchQuery) {
    //     queryParams.append('search', searchQuery);
    // }
    const queryString = queryParams.toString();
    if (queryString) {
        fetchUrl += `?${queryString}`;
    }


    try {
      const response = await fetch(fetchUrl, { credentials: 'include' }); // Include credentials if needed
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // The backend might return paginated results, handle that if needed
      // Assuming for now it returns a list or an object with a 'results' key
      const books = Array.isArray(data) ? data : data.results || [];
      console.log("Fetched book data:", books);

      // Sorting can still be done client-side if desired, or use backend ordering (?ordering=...)
      const sortedBooks = books.sort((a: Book, b: Book) => {
         // Example: Sort by title after fetching
         return a.title.localeCompare(b.title);
      });

      setBookList(sortedBooks);
    } catch (err: any) {
      console.error("Error fetching books:", err);
      setError(err.message || "Failed to load books.");
      setBookList([]); // Clear list on error
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory]); // Depend on category filter

  // Fetch books on initial load and when category changes
  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  // --- Action Handlers ---

  const handleRemoveBook = async (bookId: number) => {
    const bookToRemove = bookList.find(b => b.id === bookId);
    if (!bookToRemove) return;

    if (!window.confirm(`Are you sure you want to remove "${bookToRemove.title}"?`)) return;

    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token.");
      return;
    }

    try {
      // Use the new DELETE endpoint
      const response = await fetch(`/api/books/${bookId}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
      });

      if (response.ok) {
        // Check for 204 No Content or success message
        if (response.status === 204) {
             alert(`Book "${bookToRemove.title}" removed successfully.`);
        } else {
             const data = await response.json(); // Try parsing if not 204
             alert(data.message || `Book "${bookToRemove.title}" removed successfully.`);
        }
        // Remove from local state
        setBookList((prevBooks) => prevBooks.filter((book) => book.id !== bookId));
      } else {
        let errorMsg = `Failed to remove book. Status: ${response.status}`;
        try {
            const errData = await response.json();
            errorMsg = errData.detail || JSON.stringify(errData) || errorMsg;
        } catch (e) { /* Ignore if response not JSON */ }
        throw new Error(errorMsg);
      }
    } catch (error: any) {
      console.error("Error removing book:", error);
      alert(`Error removing book: ${error.message}`);
    }
  };

  const handleCreateBook = () => {
    setShowAddBookForm(!showAddBookForm);
    setShowEditBookForm(false);
    setEditingBook(null);
  };

  const handleBookCreated = () => {
    fetchBooks(); // Refresh book list after creation
    setShowAddBookForm(false);
  };

  const handleEditBook = (book: Book) => {
    setEditingBook(book);
    setShowEditBookForm(true);
    setShowAddBookForm(false);
  };

  const handleBookUpdated = (updatedBook: Book) => {
     // Option 1: Refresh the whole list
     // fetchBooks();
     // Option 2: Update locally (faster UI)
     setBookList((prevBooks) =>
       prevBooks.map((book) => (book.id === updatedBook.id ? updatedBook : book))
     );
    setShowEditBookForm(false);
    setEditingBook(null);
  };

  const handleEditFormCancel = () => {
    setShowEditBookForm(false);
    setEditingBook(null);
  };

  // Combined handler for Borrow/Return actions
  const handleBorrowReturn = async (book: Book) => {
    if (!currentUser) {
      alert("Please log in to borrow or return books.");
      return;
    }

    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token.");
      return;
    }

    // Determine action and endpoint
    const isReturning = !book.available && book.borrower_id === currentUser.id;
    const endpoint = isReturning
      ? `/api/books/${book.id}/return/`
      : `/api/books/${book.id}/borrow/`;
    const actionVerb = isReturning ? "return" : "borrow";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        // No body needed for these specific endpoints based on views.py
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to ${actionVerb} book: HTTP status ${response.status}`);
      }

      const data = await response.json();
      alert(data.message || `Book ${actionVerb}ed successfully!`);

      // Update the specific book in the local state immutably
      setBookList((prevBooks) =>
        prevBooks.map((b) =>
          b.id === book.id ? { ...b, ...data.book } : b // Use updated book data from response
        )
      );

    } catch (error: any) {
      console.error(`Error ${actionVerb}ing book:`, error);
      alert(`Error: ${error.message}`);
    }
  };

  // Client-side search filtering (can be moved to backend later)
  const filteredBooks = bookList.filter((book: Book) =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    book.author.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Slider settings
  const settings = {
    dots: true,
    infinite: filteredBooks.length > 4, // Only infinite if more slides than shown
    speed: 800,
    slidesToShow: 4,
    slidesToScroll: 2,
    responsive: [
       { breakpoint: 1200, settings: { slidesToShow: 3, infinite: filteredBooks.length > 3 } },
       { breakpoint: 900, settings: { slidesToShow: 2, infinite: filteredBooks.length > 2 } },
       { breakpoint: 600, settings: { slidesToShow: 1, infinite: filteredBooks.length > 1 } },
    ],
  };

  // Handler for category dropdown change
  const handleCategoryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCategory(event.target.value);
    // fetchBooks will be called by useEffect due to dependency change
  };

  const toggleBorrowedBooksView = () => {
    setShowBorrowedBooks(!showBorrowedBooks);
    // Hide Add/Edit forms when switching views
    setShowAddBookForm(false);
    setShowEditBookForm(false);
    setEditingBook(null);
  };

  return (
    <div className="principal-page-container"> {/* Added a container class */}
      {/* Search bar */}
      <div className="search-filter-container"> {/* Container for search and filter */}
        <div className="search-container">
          <input
            type="text"
            placeholder="Search books by title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-bar"
          />
        </div>
        {/* Category Dropdown */}
        <div className="category-container">
          <label htmlFor="category-select">Filter by Category:</label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={handleCategoryChange}
            className="category-select" // Added class for styling
          >
            {bookCategories.map((cat) => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Action Buttons Container */}
      <div className="action-buttons-container">
          {/* Create book button for Admins and Librarians */}
          {userType && (userType === "AD" || userType === "LB") && (
            <button onClick={handleCreateBook} className="button button-create">
              {showAddBookForm ? "Hide Add Form" : "Add New Book"}
            </button>
          )}
          {/* Borrowed Books View Button */}
          {currentUser && ( // Show if user is logged in
            <button onClick={toggleBorrowedBooksView} className="button button-toggle-borrowed">
              {showBorrowedBooks ? "Show Book Catalog" : "View My Borrowed Books"}
            </button>
          )}
      </div>


      {/* Add/Edit Forms (conditionally rendered) */}
      {showAddBookForm && userType && (userType === "AD" || userType === "LB") && (
          <div className="form-container">
              <AddBookForm onBookCreated={handleBookCreated} />
          </div>
      )}
      {showEditBookForm && editingBook && userType && (userType === "AD" || userType === "LB") && (
          <div className="form-container">
              <EditBookForm book={editingBook} onBookUpdated={handleBookUpdated} onCancel={handleEditFormCancel} />
          </div>
      )}

      {/* Content Area: Borrowed Books List OR Book Catalog */}
      <div className="content-area">
          {isLoading ? (
              <p>Loading...</p>
          ) : error ? (
              <p className="error-message">{error}</p>
          ) : showBorrowedBooks ? (
              // Borrowed Books List Component
              currentUser && <BorrowedBooksList /> // Pass necessary props if any
          ) : (
              // Book Catalog Carousel/List
              <div className="carousel-container">
                  {filteredBooks.length > 0 ? (
                      filteredBooks.length > 1 ? ( // Use Slider only if more than 1 book
                          <Slider {...settings}>
                              {filteredBooks.map((book: Book) => (
                                  <BookCard
                                      key={book.id}
                                      book={book}
                                      onBorrowReturn={handleBorrowReturn} // Pass combined handler
                                      currentUser={currentUser}
                                      onEditBook={handleEditBook} // Pass edit handler
                                      onRemoveBook={handleRemoveBook} // Pass remove handler
                                  />
                              ))}
                          </Slider>
                      ) : ( // Display single book without Slider
                          <div className="single-book-container">
                              <BookCard
                                  book={filteredBooks[0]}
                                  onBorrowReturn={handleBorrowReturn}
                                  currentUser={currentUser}
                                  onEditBook={handleEditBook}
                                  onRemoveBook={handleRemoveBook}
                              />
                          </div>
                      )
                  ) : (
                      <p className="no-results">No books found matching your criteria.</p>
                  )}
              </div>
          )}
      </div>
    </div>
  );
};

export default BookDisplayPage;