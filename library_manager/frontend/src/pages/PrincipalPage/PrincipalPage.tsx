import React, { useState, useEffect, useCallback } from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./PrincipalPage.css";
import AddBookForm from "../../components/AddBookForm/AddBookForm";
import EditBookForm from "../../components/EditBookForm/EditBookForm";
import BookCard from "../../components/BookCard/BookCard";
import BorrowedBooksList from "../../components/BorrowedBooksList/BorrowedBooksList";
import { useAuth } from "../../context/AuthContext";
// <<< ADD: Import shared types >>>
import { Book, PaginatedResponse } from '../../types/models'; // Adjust path if needed



const BookDisplayPage: React.FC = () => {
  const { currentUser, userType, getCSRFToken } = useAuth();
  const [bookList, setBookList] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddBookForm, setShowAddBookForm] = useState(false);
  const [showEditBookForm, setShowEditBookForm] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showBorrowedBooks, setShowBorrowedBooks] = useState(false);

  const bookCategories = [
    { value: '', label: 'All Categories' }, { value: 'CK', label: 'Cooking' },
    { value: 'CR', label: 'Crime' }, { value: 'MY', label: 'Mystery' },
    { value: 'SF', label: 'Science Fiction' }, { value: 'FAN', label: 'Fantasy' },
    { value: 'HIS', label: 'History' }, { value: 'ROM', label: 'Romance' },
    { value: 'TXT', label: 'Textbook' },
  ];

  const fetchBooks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    let fetchUrl = '/api/books/';
    const queryParams = new URLSearchParams();
    if (selectedCategory) queryParams.append('category', selectedCategory);
    if (searchQuery) queryParams.append('search', searchQuery);
    queryParams.append('ordering', 'title');

    const queryString = queryParams.toString();
    if (queryString) fetchUrl += `?${queryString}`;

    try {
      const response = await fetch(fetchUrl, { credentials: 'include' });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: PaginatedResponse<Book> | Book[] = await response.json();
      const books: Book[] = 'results' in data ? data.results : data;
      console.log("Fetched book data:", books); // Check if image_url is present
      setBookList(books);
    } catch (err: any) {
      console.error("Error fetching books:", err);
      setError(err.message || "Failed to load books.");
      setBookList([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, searchQuery]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  // --- Action Handlers ---
  const handleRemoveBook = async (bookId: number) => {
    const bookToRemove = bookList.find(b => b.id === bookId);
    if (!bookToRemove) return;
    if (!window.confirm(`Are you sure you want to remove "${bookToRemove.title}"?`)) return;
    const csrfToken = await getCSRFToken();
    if (!csrfToken) { alert("Error: Could not verify security token."); return; }

    try {
      const response = await fetch(`/api/books/${bookId}/`, {
        method: "DELETE", headers: { "X-CSRFToken": csrfToken }, credentials: "include",
      });
      if (response.ok || response.status === 204) {
        alert(`Book "${bookToRemove.title}" removed successfully.`);
        setBookList((prevBooks) => prevBooks.filter((book) => book.id !== bookId));
      } else {
        let errorMsg = `Failed to remove book. Status: ${response.status}`;
        try { const errData = await response.json(); errorMsg = errData.detail || JSON.stringify(errData) || errorMsg; } catch (e) { /* Ignore */ }
        throw new Error(errorMsg);
      }
    } catch (error: any) {
      console.error("Error removing book:", error); alert(`Error removing book: ${error.message}`);
    }
  };

  const handleCreateBook = () => { setShowAddBookForm(!showAddBookForm); setShowEditBookForm(false); setEditingBook(null); };
  const handleBookCreated = () => { fetchBooks(); setShowAddBookForm(false); };
  const handleEditBook = (book: Book) => { setEditingBook(book); setShowEditBookForm(true); setShowAddBookForm(false); };
  const handleBookUpdated = (updatedBook: Book) => { fetchBooks(); setShowEditBookForm(false); setEditingBook(null); };
  const handleEditFormCancel = () => { setShowEditBookForm(false); setEditingBook(null); };

  const handleBorrowReturn = async (book: Book) => {
    if (!currentUser) { alert("Please log in to borrow or return books."); return; }
    const csrfToken = await getCSRFToken();
    if (!csrfToken) { alert("Error: Could not verify security token."); return; }

    const isReturning = !book.available && book.borrower_id === currentUser.id;
    const endpoint = isReturning ? `/api/books/${book.id}/return/` : `/api/books/${book.id}/borrow/`;
    const actionVerb = isReturning ? "return" : "borrow";

    try {
      const response = await fetch(endpoint, {
        method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken }, credentials: "include",
      });
      if (!response.ok) { const errorData = await response.json(); throw new Error(errorData.error || `Failed to ${actionVerb} book: HTTP status ${response.status}`); }
      const data = await response.json();
      alert(data.message || `Book ${actionVerb}ed successfully!`);
      // Refresh the specific book in state using the response data
       setBookList((prevBooks) =>
         prevBooks.map((b) => (b.id === book.id ? { ...b, ...data.book } : b))
       );
      // Consider refreshing BorrowedBooksList if visible
    } catch (error: any) {
      console.error(`Error ${actionVerb}ing book:`, error); alert(`Error: ${error.message}`);
    }
  };

  const filteredBooks = bookList; // Use backend filtering/search

  const settings = {
    dots: true, infinite: filteredBooks.length > 4, speed: 800, slidesToShow: 4, slidesToScroll: 2,
    responsive: [
      { breakpoint: 1200, settings: { slidesToShow: 3, slidesToScroll: 2, infinite: filteredBooks.length > 3 } },
      { breakpoint: 900, settings: { slidesToShow: 2, slidesToScroll: 1, infinite: filteredBooks.length > 2 } },
      { breakpoint: 600, settings: { slidesToShow: 1, slidesToScroll: 1, infinite: filteredBooks.length > 1 } },
    ],
  };

  const handleCategoryChange = (event: React.ChangeEvent<HTMLSelectElement>) => { setSelectedCategory(event.target.value); };
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => { setSearchQuery(event.target.value); };
  const toggleBorrowedBooksView = () => { setShowBorrowedBooks(!showBorrowedBooks); setShowAddBookForm(false); setShowEditBookForm(false); setEditingBook(null); };

  return (
    <div className="principal-page-container">
      <div className="search-filter-container">

        <div className="category-container">
          <label htmlFor="category-select">Filter by Category:</label>
          <select id="category-select" value={selectedCategory} onChange={handleCategoryChange} className="category-select">
            {bookCategories.map((cat) => ( <option key={cat.value} value={cat.value}>{cat.label}</option> ))}
          </select>
        </div>
        <div className="search-container">
          <input type="text" placeholder="Search books by title or author..." value={searchQuery} onChange={handleSearchChange} className="search-bar" />
        </div>  
      </div>

      <div className="action-buttons-container">
        {userType && (userType === "AD" || userType === "LB") && (
          <button onClick={handleCreateBook} className="button-principal">
            {showAddBookForm ? "Hide Add Form" : "Add New Book"}
          </button>
        )}
        {currentUser && (
          <button onClick={toggleBorrowedBooksView} className="button-principal">
            {showBorrowedBooks ? "Show Book Catalog" : "View Borrowed Books"}
          </button>
        )}
      </div>

      {showAddBookForm && userType && (userType === "AD" || userType === "LB") && ( <div className="form-container"><AddBookForm onBookCreated={handleBookCreated} /></div> )}
      {showEditBookForm && editingBook && userType && (userType === "AD" || userType === "LB") && ( <div className="form-container"><EditBookForm book={editingBook} onBookUpdated={handleBookUpdated} onCancel={handleEditFormCancel} /></div> )}

      <div className="content-area">
        {isLoading ? ( <p>Loading...</p> ) : error ? ( <p className="error-message">{error}</p> ) : showBorrowedBooks ? (
          currentUser && <BorrowedBooksList />
        ) : (
          <div className="carousel-container">
            {filteredBooks.length > 0 ? (
              filteredBooks.length > 1 ? (
                <Slider {...settings}>
                  {filteredBooks.map((book: Book) => (
                    <BookCard key={book.id} book={book} onBorrowReturn={handleBorrowReturn} currentUser={currentUser} onEditBook={handleEditBook} onRemoveBook={handleRemoveBook} />
                  ))}
                </Slider>
              ) : (
                <div className="single-book-container">
                  <BookCard book={filteredBooks[0]} onBorrowReturn={handleBorrowReturn} currentUser={currentUser} onEditBook={handleEditBook} onRemoveBook={handleRemoveBook} />
                </div>
              )
            ) : ( <p className="no-results">No books found matching your criteria.</p> )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookDisplayPage;