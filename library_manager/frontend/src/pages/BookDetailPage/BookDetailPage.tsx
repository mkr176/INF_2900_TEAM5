import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./BookDetailPage.css";

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
  borrower_id: number | null;
  due_date: string;
}

const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<Book | null>(null);

  useEffect(() => {
    fetch(`/api/book/${id}/`)
      .then((response) => response.json())
      .then((data) => setBook(data))
      .catch((error) => console.error("Error fetching book details:", error));
  }, [id]);

  if (!book) {
    return <p>Loading book details...</p>;
  }

  return (
    <div className="book-detail-container">
      <h1>{book.title}</h1>
      <img src={book.image} alt={book.title} className="book-detail-image" />
      <p><strong>Author:</strong> {book.author}</p>
      <p><strong>Category:</strong> {book.category}</p>
      <p><strong>Language:</strong> {book.language}</p>
      <p><strong>Condition:</strong> {book.condition}</p>
      <p><strong>ISBN:</strong> {book.isbn}</p>
      <p>
        <strong>Availability:</strong>{" "}
        <span className={book.available ? "available-text" : "unavailable-text"}>
          {book.available ? "Available" : `Checked out until ${new Date(book.due_date).toLocaleDateString()}`}
        </span>
      </p>
    </div>
  );
};

export default BookDetailPage;
