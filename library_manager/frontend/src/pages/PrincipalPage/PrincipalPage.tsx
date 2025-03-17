import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./PrincipalPage.css";
import AddBookForm from "../../components/AddBookForm/AddBookForm"; // ✅ Import AddBookForm

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
  const [showAddBookForm, setShowAddBookForm] = useState(false); // State to control form visibility


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

  const handleViewDetails = (book: Book) => {
    alert(`${book.title}`);
  };

  const handleCreateBook = () => {
    setShowAddBookForm(!showAddBookForm); // Toggle form visibility
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
        // Update book availability in the local state
        setBookList((prevBooks) => {
          const updatedBooks = prevBooks.map((b) =>
            b.id === book.id ? { ...b, available: data.book.available, borrower_id: data.book.borrower_id } : b
          );
          console.log("Updated bookList:", updatedBooks); // Log updated bookList
          return updatedBooks;
        });
        alert(data.message); // Show success or return message
      })
      .catch((error) => {
        console.error("Error borrowing/returning book:", error);
        alert(`Error: ${error.message}`); // Display error message from catch
      });
  };

  const filteredBooks = bookList.filter((book: Book) =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase())
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
        return "Return Book";
      } else {
        const dueDate = new Date(book.due_date).toLocaleDateString();
        return `Unavailable until ${dueDate}`;
      }
    }
  };


  return (
    <div>
      {/* Search bar */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search books..."
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
        <AddBookForm onBookCreated={handleBookCreated} userId={currentUser.id.toString()} /> // ✅ Pass currentUser.id as prop
      )}
      {/* Book carousel */}
      <div className="carousel-container">
        {filteredBooks.length > 1 ? (
          <Slider {...settings}>
            {filteredBooks.map((book: Book) => (
              <motion.div key={book.id} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <div className="book-card">
                  <motion.img
                    src={book.image}
                    alt={book.title}
                    className="book-image"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                  />
                  <h2 className="book-title">{book.title}</h2>
                  <div className="book-actions"> {/* Container for buttons */}
                    <button onClick={() => handleViewDetails(book)} className="button button-outline view-details-button">
                      View Details
                    </button>
                    <button
                      onClick={() => handleBorrowReturn(book)}
                      className="button button-primary borrow-button"
                    >
                      {getBorrowButtonText(book)}
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </Slider>
        ) : filteredBooks.length === 1 ? (
          <div className="single-book-container">
            <div className="book-card">
              <img src={filteredBooks[0].image} alt={filteredBooks[0].title} className="book-image" />
              <h2 className="book-title">{filteredBooks[0].title}</h2>
              <div className="book-actions"> {/* Container for buttons */}
                <button onClick={() => handleViewDetails(filteredBooks[0])} className="button button-outline view-details-button">
                  View Details
                </button>
                <button
                  onClick={() => handleBorrowReturn(filteredBooks[0])}
                  className="button button-primary borrow-button"
                >
                  {getBorrowButtonText(filteredBooks[0])}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <p className="no-results">No books found</p>
        )}
      </div>
    </div>
  );
};

export default BookDisplayPage;
