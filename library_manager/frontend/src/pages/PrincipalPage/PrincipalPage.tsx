import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./PrincipalPage.css";
import AddBookForm from "../../components/AddBookForm/AddBookForm";
import EditBookForm from "../../components/EditBookForm/EditBookForm"; // ✅ Import EditBookForm
import BookCard from "./BookCard"; // ✅ Import BookCard component


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
  borrower_id: number | null; // Add borrower_id to Book interface
  due_date: string; // Ensure due_date is a string to handle date format from backend
  publisher: string;
  publication_year: number;
  copy_number: string;
  storage_location: string; // Add storage_location property
}
interface People {
  id: number;
  username: string;
  email: string;
  type: string;
  numberofbooks: number;
  password?: string; // just for type compatibility, not actually used in frontend
}


const BookDisplayPage: React.FC = () => {
  const [bookList, setBookList] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentUser, setCurrentUser] = useState<People | null>(null);
  const [showAddBookForm, setShowAddBookForm] = useState(false); // State to control AddBookForm visibility
  const [flippedBooks, setFlippedBooks] = useState<{ [key: number]: boolean }>({});
  const [showEditBookForm, setShowEditBookForm] = useState(false); // ✅ State to control EditBookForm visibility
  const [editingBook, setEditingBook] = useState<Book | null>(null); // ✅ State to hold book being edited


  useEffect(() => {
    fetch("/api/principal/")
      .then((response) => response.json())
      .then((data) => {
        console.log("Initial book data:", data); // Log initial book data
        setBookList(data);
      })
      .catch((error) => console.error("Error fetching books:", error));
    fetch("/api/current_user/")
      .then((response) => response.json())
      .then((data) => setCurrentUser(data))
      .catch((error) => console.error("Error fetching current user:", error));
  }, []);


  const handleRemoveBook = (bookId: number) => {
    if (!window.confirm("Are you sure you want to remove this book?")) return;

    fetch(`/api/book/${bookId}/`, { method: "DELETE" })
      .then((response) => {
        if (!response.ok) {
          console.error("HTTP error!", response); // Log the entire response for more details
          throw new Error(`Failed to remove book: HTTP status ${response.status}`);
        }
        return response.json(); // Parse JSON here
      })
      .then((data) => {
        console.log("Book removal successful:", data); // Log success data
        setBookList((prevBooks) => prevBooks.filter((book) => book.id !== bookId));
      })
      .catch((error) => {
        console.error("Error removing book:", error); // Keep error logging
        alert(`Error removing book: ${error.message}`); // Keep alert
      });
  };
  const handleViewDetails = (book: Book) => {
    alert(`${book.title}`);
  };

  const handleCreateBook = () => {
    setShowAddBookForm(!showAddBookForm); // Toggle form visibility
    setShowEditBookForm(false); // Ensure Edit form is hidden when Add form is shown
  };

  const handleBookCreated = () => {
    // Callback function to refresh book list after book creation
    fetch("/api/principal/")
      .then((response) => response.json())
      .then((data) => {
        setBookList(data); // Update book list
      })
      .catch((error) => console.error("Error fetching books:", error));
    setShowAddBookForm(false); // Optionally hide the form after successful creation
  };

  const handleBookUpdated = (updatedBook: Book) => {
    setBookList((prevBooks) =>
      prevBooks.map((book) => (book.id === updatedBook.id ? updatedBook : book))
    );
    setShowEditBookForm(false);
    setEditingBook(null);
  };

  const handleEditBook = (book: Book) => { // ✅ Function to handle Edit Book button click
    setEditingBook(book); // Set the book to be edited
    setShowEditBookForm(true); // Show the EditBookForm
    setShowAddBookForm(false); // Ensure Add form is hidden when Edit form is shown
  };

  const handleEditFormCancel = () => { // ✅ Function to handle canceling Edit Book form
    setShowEditBookForm(false); // Hide EditBookForm
    setEditingBook(null); // Clear editing book
  };



  const handleBorrowReturn = (book: Book) => {
    if (!currentUser) {
      alert("Please log in to borrow or return books.");
      return;
    }

    fetch("/api/borrow_book/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ book_id: book.id, user_id: currentUser.id }),
    })
      .then((response) => {
        if (!response.ok) { // Check response.ok here
          return response.json().then(err => { // Parse error response as JSON
            throw new Error(err.message || 'Failed to borrow/return book'); // Throw error with message
          });
        }
        return response.json(); // Proceed to parse JSON if response is ok
      })
      .then((data) => {
        console.log("Borrow/Return API response:", data);
        console.log("BookList before update:", bookList); // Log bookList before update

        // Update book availability in the local state - IMMUTABLE UPDATE
        setBookList((prevBooks) => {
          console.log("prevBooks inside setBookList map:", prevBooks); // Log prevBooks inside map
          const updatedBooks = prevBooks.map((b) =>
            b.id === book.id ? { ...b, ...data.book } : b // Use spread operator to update book properties
          );
          console.log("Updated bookList:", updatedBooks); // Log updated bookList
          return updatedBooks;
        });
        console.log("BookList after update:", bookList); // Log bookList after update (should show updated value in next render)
        alert(data.message); // Show success or return message
      })
      .catch((error) => {
        console.error("Error borrowing/returning book:", error);
        alert(`Error: ${error.message}`); // Display error message from catch
      });
  };

  const filteredBooks = bookList.filter((book: Book) =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase()) || book.author.toLowerCase().includes(searchQuery.toLowerCase())

  );

  const settings = {
    dots: true,
    infinite: true,
    speed: 800,
    slidesToShow: 4,
    slidesToScroll: 2,
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 3,
        },
      },
      {
        breakpoint: 900, // For smaller screens
        settings: {
          slidesToShow: 2,
        },
      },
    ],
  };

  const getBorrowButtonText = (book: Book): string => {
    if (book.available) {
      return "Borrow Book";
    } else {
      if (currentUser && book.borrower_id === currentUser.id) {
        const dueDate = new Date(book.due_date).toLocaleDateString();
        return `Return Book - due date: ${dueDate}`;
      } else {
        const dueDate = new Date(book.due_date).toLocaleDateString();
        return `Unavailable until ${dueDate}`;
      }
    }
  };



  const handleMouseEnter = (bookId: number) => {
    setTimeout(() => {
      setFlippedBooks((prev) => ({ ...prev, [bookId]: true }));
    }, 150);
  };

  const handleMouseLeave = (bookId: number) => {
    setTimeout(() => {
      setFlippedBooks((prev) => ({ ...prev, [bookId]: false }));
    }, 150);
  };



  return (
    <div>
      {/* Search bar */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search books by title or author..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-bar"
        />
      </div>
      {/* Create book button for Admins and Librarians */}
      {currentUser && (currentUser.type === "AD" || currentUser.type === "LB") && (
        <div className="create-book-container">
          <button onClick={handleCreateBook} className="button button-primary">
            {showAddBookForm ? "Hide Book Form" : "Create Book"} {/* Toggle button text */}
          </button>
        </div>
      )}
      {/* Conditionally render AddBookForm */}
      {showAddBookForm && currentUser && ( // ✅ Ensure currentUser is available
        <AddBookForm onBookCreated={handleBookCreated} /> // ✅ Pass onBookCreated callback
      )}
      {/* Conditionally render EditBookForm */}
      {showEditBookForm && editingBook && currentUser && ( // ✅ Render EditBookForm when showEditBookForm is true
        <EditBookForm
          book={editingBook}
          onBookUpdated={handleBookUpdated} // ✅ Pass onBookUpdated callback
          onCancel={handleEditFormCancel} // ✅ Pass onCancel callback
        />
      )}
      {/* Book carousel */}
      <div className="carousel-container">
        {filteredBooks.length > 1 ? (
          <Slider {...settings}>
            {filteredBooks.map((book: Book) => (
              <BookCard
                key={book.id}
                book={book}
                onBorrow={() => handleBorrowReturn(book)}
                currentUser={currentUser} // ✅ Pass currentUser prop to BookCard
                onEditBook={() => handleEditBook(book)} // ✅ Pass handleEditBook to BookCard
                onRemoveBook={handleRemoveBook}
              />
            ))}
          </Slider>
        ) : filteredBooks.length === 1 ? (
          <div className="single-book-container">
            <BookCard
              book={filteredBooks[0]}
              onBorrow={() => handleBorrowReturn(filteredBooks[0])}
              currentUser={currentUser} // ✅ Pass currentUser prop to BookCard
              onEditBook={() => handleEditBook(filteredBooks[0])} // ✅ Pass handleEditBook to BookCard
              onRemoveBook={handleRemoveBook}
            />
          </div>
        ) : (
          <p className="no-results">No books found</p>
        )}
      </div>

    </div>
  );
};

export default BookDisplayPage;
