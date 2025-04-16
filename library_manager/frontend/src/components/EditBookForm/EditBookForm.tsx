import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext'; // Import useAuth for CSRF token
import "../AddBookForm/AddBookForm.css"; // Reuse AddBookForm styles

// Updated Book interface based on BookSerializer (include relevant fields)
// REMOVED user_id and adjusted nullable types
interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string; // Code (e.g., 'CK')
    language: string;
    condition: string; // Code (e.g., 'GD')
    available: boolean; // Read-only, managed by borrow/return
    storage_location: string | null;
    publisher: string | null;
    publication_year: number | null;
    copy_number: number | null;
    // Read-only fields not typically edited here:
    // category_display?: string; // Optional as it might not be passed if not needed for edit
    // condition_display?: string; // Optional
    // borrower?: string | null;
    // borrower_id?: number | null;
    // borrow_date?: string | null;
    // due_date?: string | null; // Should be string | null if present
    // added_by?: string | null;
    // added_by_id?: number | null;
}


interface EditBookFormProps {
    book: Book;
    onBookUpdated: (updatedBook: Book) => void; // Callback after successful update
    onCancel: () => void; // Callback to cancel editing
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
    const { getCSRFToken } = useAuth(); // Get CSRF token function

    // Initialize state from the book prop
    const [title, setTitle] = useState(book.title || '');
    const [author, setAuthor] = useState(book.author || '');
    const [isbn, setIsbn] = useState(book.isbn || ''); // ISBN might not be editable usually, but allow for now
    const [category, setCategory] = useState(book.category || '');
    const [language, setLanguage] = useState(book.language || '');
    const [condition, setCondition] = useState(book.condition || '');
    const [storageLocation, setStorageLocation] = useState(book.storage_location || '');
    const [publisher, setPublisher] = useState(book.publisher || '');
    // Use string for input state, parse on submit
    const [publicationYear, setPublicationYear] = useState<string>(book.publication_year?.toString() || '');
    const [copyNumber, setCopyNumber] = useState<string>(book.copy_number?.toString() || '');
    // 'available' is read-only and not included in the form state

    // Update state if the book prop changes (e.g., user selects a different book to edit)
    useEffect(() => {
        setTitle(book.title || '');
        setAuthor(book.author || '');
        setIsbn(book.isbn || '');
        setCategory(book.category || '');
        setLanguage(book.language || '');
        setCondition(book.condition || '');
        setStorageLocation(book.storage_location || '');
        setPublisher(book.publisher || '');
        setPublicationYear(book.publication_year?.toString() || '');
        setCopyNumber(book.copy_number?.toString() || '');
    }, [book]);


    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Error: Could not verify security token. Please refresh and try again.");
            return;
        }

        // --- Prepare Payload ---
        // Only include fields that are meant to be updated and are writable in the serializer
        const payload: Partial<Book> = {
            // Include id in payload for PATCH? No, it's in the URL.
            title,
            author,
            isbn, // Assuming ISBN can be updated (might need backend adjustment if unique constraint causes issues on update)
            category,
            language,
            condition,
            storage_location: storageLocation || null, // Send null if empty
            publisher: publisher || null, // Send null if empty
            // Parse year and copy number, send null if invalid or empty
            publication_year: publicationYear ? parseInt(publicationYear, 10) || null : null,
            copy_number: copyNumber ? parseInt(copyNumber, 10) || null : null,
            // DO NOT SEND read-only fields like 'available', 'borrower', 'borrower_id', 'added_by', etc.
        };

        // Basic validation for parsed numbers
        if (publicationYear && isNaN(payload.publication_year as number)) {
             alert("Please enter a valid publication year.");
             return;
        }
         if (copyNumber && isNaN(payload.copy_number as number)) {
             alert("Please enter a valid copy number.");
             return;
        }


        try {
            // Use the correct endpoint and PATCH method for partial updates
            const response = await fetch(`/api/books/${book.id}/`, {
                method: 'PATCH', // Use PATCH
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Include CSRF token
                },
                body: JSON.stringify(payload),
                credentials: 'include',
            });

            if (response.ok) {
                const updatedBookData: Book = await response.json(); // Get updated book data from response
                alert('Book updated successfully!');
                // Ensure the data passed back matches the expected interface
                onBookUpdated(updatedBookData); // Pass updated data back to parent
                // No need to call onCancel here, parent component handles closing the form via onBookUpdated
            } else {
                // Handle validation errors or other issues
                let errorMsg = 'Error updating book';
                try {
                const errorData = await response.json();
                    if (typeof errorData === 'object' && errorData !== null) {
                        errorMsg = Object.entries(errorData)
                            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('\n');
                    } else if (errorData.detail) {
                        errorMsg = errorData.detail;
                    }
                } catch (e) {
                    errorMsg = `Error updating book (Status: ${response.status})`;
                }
                alert(errorMsg);
            }
        } catch (error) {
            console.error('Error updating book:', error);
            alert('Failed to update book. Please check console for details.');
        }
    };

    return (
        // Reuse add-book-form styles, maybe rename CSS class later if needed
        <form onSubmit={handleSubmit} className="add-book-form edit-book-form">
            <h2>Edit Book: {book.title}</h2>

            <label htmlFor="edit-title">Title:</label>
            <input type="text" id="edit-title" value={title} onChange={(e) => setTitle(e.target.value)} required />

            <label htmlFor="edit-author">Author:</label>
            <input type="text" id="edit-author" value={author} onChange={(e) => setAuthor(e.target.value)} required />

            <label htmlFor="edit-isbn">ISBN:</label>
            <input type="text" id="edit-isbn" value={isbn} onChange={(e) => setIsbn(e.target.value)} required />

            <label htmlFor="edit-category">Category:</label>
            <select id="edit-category" value={category} onChange={(e) => setCategory(e.target.value)} required>
                {bookCategories.map((cat) => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
            </select>

            <label htmlFor="edit-language">Language:</label>
            <input type="text" id="edit-language" value={language} onChange={(e) => setLanguage(e.target.value)} required />

            <label htmlFor="edit-condition">Condition:</label>
            <select id="edit-condition" value={condition} onChange={(e) => setCondition(e.target.value)} required>
                {bookConditions.map((cond) => (
                    <option key={cond.value} value={cond.value}>{cond.label}</option>
                ))}
            </select>

            <label htmlFor="edit-storageLocation">Storage Location:</label>
            <input type="text" id="edit-storageLocation" value={storageLocation} onChange={(e) => setStorageLocation(e.target.value)} />

            <label htmlFor="edit-publisher">Publisher:</label>
            <input type="text" id="edit-publisher" value={publisher} onChange={(e) => setPublisher(e.target.value)} />

            <label htmlFor="edit-publicationYear">Publication Year:</label>
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="edit-publicationYear" value={publicationYear} onChange={(e) => setPublicationYear(e.target.value)} />

            <label htmlFor="edit-copyNumber">Copy Number:</label>
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="edit-copyNumber" value={copyNumber} onChange={(e) => setCopyNumber(e.target.value)} />

            {/* 'Available' field is read-only and not editable here */}
            {/* <label htmlFor="available">Available:</label> */}
            {/* <input type="checkbox" id="available" checked={available} onChange={(e) => setAvailable(e.target.checked)} /> */}

            <div className="edit-form-buttons">
            <button type="submit">Update Book</button>
                 <button type="button" onClick={onCancel} className="cancel-button">Cancel</button>
            </div>
        </form>
    );
};

export default EditBookForm;