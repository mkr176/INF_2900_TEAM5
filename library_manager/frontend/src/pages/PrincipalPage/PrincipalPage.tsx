import React, { useState,useEffect } from "react";
import { motion } from "framer-motion";
import "./PrincipalPage.css"; 


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
}

const BookDisplayPage: React.FC = () => {
  const [bookList, setBookList] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");


useEffect(() => {
    fetch("/api/principal/")
      .then((response) => response.json())
      .then((data) => setBookList(data))
      .catch((error) => console.error("Error fetching books:", error));
  }, []);

  const handleViewDetails = (book: Book) => {
    alert(`${book.title}`);
  };

  // 🔎 Filtrar libros según la búsqueda
  const filteredBooks = bookList.filter((book:Book) =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      {/* 🔎 Barra de búsqueda */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search books..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-bar"
        />
      </div>

      <div className="book-grid">
        {filteredBooks.length > 0 ? (
          filteredBooks.map((book:Book) => (
            <motion.div
              key={book.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
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
                <div>
                  <button
                    onClick={() => handleViewDetails(book)}
                    className="button button-outline"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <p className="no-results">No books found</p>
        )}
      </div>
    </div>
  );
};

export default BookDisplayPage;