import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import EditBookForm from "../../components/EditBookForm/EditBookForm";

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
  storage_location: string;
  publisher: string;
  publication_year: number;
  copy_number: string;
}

const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<Book | null>(null);
  const [refresh, setRefresh] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);

  const fetchBookDetails = () => {
    fetch(`/api/book/${id}/`)
      .then((response) => response.json())
      .then((data) => setBook(data))
      .catch((error) => console.error("Error fetching book details:", error));
  };

  useEffect(() => {
    fetchBookDetails();
  }, [id, refresh]); // Re-fetch when refresh state changes

  const handleBookUpdated = () => {
    setRefresh((prev) => !prev); // Trigger refresh
    setShowEditForm(false); // Close edit form
  };

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

      <button onClick={() => setShowEditForm(true)}>Edit Book</button>

      {showEditForm && (
        <EditBookForm 
          book={book} 
          onBookUpdated={handleBookUpdated} 
          onCancel={() => setShowEditForm(false)}
        />
      )}
    </div>
  );
};

export default BookDetailPage;
