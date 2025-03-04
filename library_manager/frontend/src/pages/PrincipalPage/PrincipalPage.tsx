import React, { useState } from "react";
import { motion } from "framer-motion";
import "./PrincipalPage.css"; 

const books = [
  {
    id: 1,
    title: "En Familia con Karlos Arguiñano",
    summary: "Delicious recipes for home cooking by Karlos Arguiñano.",
    image: "static/images/libroCocina.jpg",
    reserved: false,
  },
  {
    id: 2,
    title: "The Hound of the Baskervilles",
    summary: "A classic Sherlock Holmes mystery by Arthur Conan Doyle.",
    image: "static/images/libroMisterio.jpg",
    reserved: false,
  },
  {
    id: 3,
    title: "Diez Negritos",
    summary: "A thrilling mystery novel by Agatha Christie.",
    image: "static/images/libroCrimen.jpg",
    reserved: false,
  },
];

const BookDisplayPage: React.FC = () => {
  const [bookList, setBookList] = useState(books);
  const [searchQuery, setSearchQuery] = useState("");

  const handleReserve = (id: number) => {
    setBookList((prevBooks) =>
      prevBooks.map((book) =>
        book.id === id && !book.reserved ? { ...book, reserved: true } : book
      )
    );
  };

  const handleViewDetails = (book: any) => {
    alert(`${book.title}: ${book.summary}`);
  };

  // 🔎 Filtrar libros según la búsqueda
  const filteredBooks = bookList.filter((book) =>
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
          filteredBooks.map((book) => (
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
                  <button
                    onClick={() => handleReserve(book.id)}
                    className={`button button-default ${
                      book.reserved ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                    disabled={book.reserved}
                  >
                    {book.reserved ? "Reserved" : "Reserve"}
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