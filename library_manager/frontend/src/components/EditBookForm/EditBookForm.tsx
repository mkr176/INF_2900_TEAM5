import React, { useState, useEffect } from 'react';
import "../AddBookForm/AddBookForm.css"; // ✅ Corrected import path for CSS
interface EditBookFormProps {
    book: Book;
    onBookUpdated?: () => void; // Callback after book update
    onCancel: () => void; // Callback to cancel editing
}

interface Book { // ✅ Re-define Book interface (or ideally share it)
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string;
    language: string;
    condition: string;
    available: boolean;
    storage_location: string;
    publisher: string;
    publication_year: number;
    copy_number: string;
    borrower_id: number | null;
    due_date: string;
    user_id: number;
}


const bookCategories = [ // ✅ Reuse category and condition lists
    { value: 'CK', label: 'Cooking' },
    { value: 'CR', label: 'Crime' },
    { value: 'MY', label: 'Mistery' },
    { value: 'SF', label: 'Science Fiction' },
    { value: 'FAN', label: 'Fantasy' },
    { value: 'HIS', label: 'History' },
    { value: 'ROM', label: 'Romance' },
    { value: 'TXT', label: 'Textbook' },
];

const bookConditions = [
    { value: 'NW', label: 'New' },
    { value: 'GD', label: 'Good' },
    { value: 'FR', label: 'Fair' },
    { value: 'PO', label: 'Poor' },
];


const EditBookForm: React.FC<EditBookFormProps> = ({ book, onBookUpdated, onCancel }) => {
    const [title, setTitle] = useState(book.title || '');
    const [author, setAuthor] = useState(book.author || 'Henrik Ibsen');
    const [isbn, setIsbn] = useState(book.isbn || '');
    const [category, setCategory] = useState(book.category || bookCategories[0].value);
    const [language, setLanguage] = useState(book.language || 'English');
    const [condition, setCondition] = useState(book.condition || bookConditions[0].value);
    const [storageLocation, setStorageLocation] = useState(book.storage_location || 'Shelf A1');
    const [publisher, setPublisher] = useState(book.publisher || 'Tromsø University Press');
    const [publicationYear, setPublicationYear] = useState(String(book.publication_year) || '2025'); // Convert number to string
    const [copyNumber, setCopyNumber] = useState(book.copy_number || '1');
    const [available, setAvailable] = useState(book.available || true);

    useEffect(() => { // ✅ useEffect to initialize form fields when book prop changes
        setTitle(book.title || '');
        setAuthor(book.author || 'Henrik Ibsen');
        setIsbn(book.isbn || '');
        setCategory(book.category || bookCategories[0].value);
        setLanguage(book.language || 'English');
        setCondition(book.condition || bookConditions[0].value);
        setStorageLocation(book.storage_location || 'Shelf A1');
        setPublisher(book.publisher || 'Tromsø University Press');
        setPublicationYear(String(book.publication_year) || '2025');
        setCopyNumber(book.copy_number || '1');
        setAvailable(book.available || true);
    }, [book]);


    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        const updatedBookData = {
            title,
            author,
            isbn,
            category,
            language,
            condition,
            available,
            storage_location: storageLocation, // ✅ Use camelCase 'storageLocation' here
            publisher,
            publicationYear,
            copyNumber
        };

        try {
            const response = await fetch(`/api/update_book/${book.id}/`, { // ✅ Use PUT and book.id
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedBookData),
            });

            if (response.ok) {
                alert('Book updated successfully!');
                if (onBookUpdated) {
                    onBookUpdated(); // Notify parent component about update
                }
                onCancel(); // Hide the edit form after successful update
            } else {
                const errorData = await response.json();
                alert(`Error updating book: ${errorData.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to update book. Please check console for details.');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="add-book-form"> {/* ✅ Reuse add-book-form styles */}
            <h2>Edit Book</h2>
            <label htmlFor="title">Title:</label>
            <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />

            <label htmlFor="author">Author:</label>
            <input type="text" id="author" value={author} onChange={(e) => setAuthor(e.target.value)} required />

            <label htmlFor="isbn">ISBN:</label>
            <input type="text" id="isbn" value={isbn} onChange={(e) => setIsbn(e.target.value)} required />

            <label htmlFor="category">Category:</label>
            <select id="category" value={category} onChange={(e) => setCategory(e.target.value)} required>
                {bookCategories.map((cat) => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
            </select>

            <label htmlFor="language">Language:</label>
            <input type="text" id="language" value={language} onChange={(e) => setLanguage(e.target.value)} required />

            <label htmlFor="condition">Condition:</label>
            <select id="condition" value={condition} onChange={(e) => setCondition(e.target.value)} required>
                {bookConditions.map((cond) => (
                    <option key={cond.value} value={cond.value}>{cond.label}</option>
                ))}
            </select>

            <label htmlFor="storageLocation">Storage Location:</label>
            <input type="text" id="storageLocation" value={storageLocation} onChange={(e) => setStorageLocation(e.target.value)} />

            <label htmlFor="publisher">Publisher:</label>
            <input type="text" id="publisher" value={publisher} onChange={(e) => setPublisher(e.target.value)} />

            <label htmlFor="publicationYear">Publication Year:</label>
            <input type="number" id="publicationYear" value={publicationYear} onChange={(e) => setPublicationYear(e.target.value)} />

            <label htmlFor="copyNumber">Copy Number:</label>
            <input type="number" id="copyNumber" value={copyNumber} onChange={(e) => setCopyNumber(e.target.value)} />


            <label htmlFor="available">Available:</label>
            <input type="checkbox" id="available" checked={available} onChange={(e) => setAvailable(e.target.checked)} />

            <button type="submit">Update Book</button>
            <button type="button" onClick={onCancel}>Cancel</button> {/* ✅ Cancel button */}
        </form>
    );
};

export default EditBookForm;