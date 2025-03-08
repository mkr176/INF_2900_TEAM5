import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
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
  const [bookList, setBookList] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetch("/api/get_books/")
      .then((response) => response.json())
      .then((data) => setBookList(data))
      .catch((error) => console.error("Error fetching books:", error));
  }, []);

  const handleViewDetails = (book: Book) => {
    alert(`${book.title}`);
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
        breakpoint: 900, // Para pantallas más pequeñas
        settings: {
          slidesToShow: 2,
        },
      },
    ],
  };

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

      {/* 🎠 Carrusel de libros */}
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
                  <button onClick={() => handleViewDetails(book)} className="button button-outline">
                    View Details
                  </button>
                </div>
              </motion.div>
            ))}
          </Slider>
        ) : filteredBooks.length === 1 ? (
          <div className="single-book-container">
            <div className="book-card">
              <img src={filteredBooks[0].image} alt={filteredBooks[0].title} className="book-image" />
              <h2 className="book-title">{filteredBooks[0].title}</h2>
              <button onClick={() => handleViewDetails(filteredBooks[0])} className="button button-outline">
                View Details
              </button>
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
