import React, { useState, useEffect } from 'react';
import "./AddBookForm.css"; // ✅ Import CSS for styling

interface AddBookFormProps {
    onBookCreated?: () => void; // Optional callback after book creation
}

const bookCategories = [ // Define category choices
    { value: 'CK', label: 'Cooking' },
    { value: 'CR', label: 'Crime' },
    { value: 'MY', label: 'Mistery' },
    { value: 'SF', label: 'Science Fiction' },
    { value: 'FAN', label: 'Fantasy' },
    { value: 'HIS', label: 'History' },
    { value: 'ROM', label: 'Romance' },
    { value: 'TXT', label: 'Textbook' },
];

const bookConditions = [ // Define condition choices
    { value: 'NW', label: 'New' },
    { value: 'GD', label: 'Good' },
    { value: 'FR', label: 'Fair' },
    { value: 'PO', label: 'Poor' },
];

const AddBookForm: React.FC<AddBookFormProps> = ({ onBookCreated }) => {
    const [title, setTitle] = useState('');
    const [author, setAuthor] = useState('Henrik Ibsen');
    const [isbn, setIsbn] = useState('');
    const [category, setCategory] = useState(bookCategories[0].value); // Default to first category
    const [language, setLanguage] = useState('English'); // Default value
    const [condition, setCondition] = useState(bookConditions[0].value); // Default to 'Good' (GD) - now using first condition
    const [storageLocation, setStorageLocation] = useState('Shelf A1'); // Default value
    const [publisher, setPublisher] = useState('Tromsø University Press');
    const [publicationYear, setPublicationYear] = useState('2025');
    const [copyNumber, setCopyNumber] = useState('1');
    const [available, setAvailable] = useState(true);


    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        const bookData = {
            title,
            author,
            isbn,
            category,
            language,
            condition,
            available,
            storageLocation,
            publisher,
            publicationYear,
            copyNumber
        };

        try {
            const response = await fetch('/api/create_book/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookData),
            });

            if (response.ok) {
                alert('Book created successfully!');
                // Reset form fields after successful submission
                setTitle('');
                setAuthor('');
                setIsbn('');
                setCategory(bookCategories[0].value);
                setLanguage('English');
                setCondition(bookConditions[0].value);
                setAvailable(true);
                setStorageLocation('Shelf A1');
                setPublisher('');
                setPublicationYear('');
                setCopyNumber('1');
                if (onBookCreated) {
                    onBookCreated(); // Notify parent component about book creation
                }
            } else {
                const errorData = await response.json();
                alert(`Error creating book: ${errorData.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create book. Please check console for details.');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="add-book-form">
            <h2>Add New Book</h2>
            <label htmlFor="title">Title:</label>
            <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />

            <label htmlFor="author">Author:</label>
            <input type="text" id="author" value={author} onChange={(e) => setAuthor(e.target.value)} required />

            <label htmlFor="isbn">ISBN:</label>
            <input type="text" id="isbn" value={isbn} onChange={(e) => setIsbn(e.target.value)} required />

            <label htmlFor="category">Category:</label>
            <select id="category" value={category} onChange={(e) => setCategory(e.target.value)} required>
                {bookCategories.map((cat) => (
                    <option key={cat.value} value={cat.value}>{cat.value}</option>
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

            <button type="submit">Add Book</button>
        </form>
    );
};

export default AddBookForm;