import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import "../AddBookForm/AddBookForm.css"; // Reuse styles

// Updated Book interface
interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string;
    category_display?: string;
    language: string;
    condition: string;
    condition_display?: string;
    available: boolean;
    // image?: string | null; // Original field (relative path)
    image_url?: string | null; // <<< ADD: URL for display (read-only) >>>
    storage_location: string | null;
    publisher: string | null;
    publication_year: number | null;
    copy_number: number | null;
    borrower?: string | null;
    borrower_id?: number | null;
    borrow_date?: string | null;
    due_date?: string | null;
    added_by?: string | null;
    added_by_id?: number | null;
}


interface EditBookFormProps {
    book: Book;
    onBookUpdated: (updatedBook: Book) => void;
    onCancel: () => void;
}


const bookCategories = [
    { value: 'CK', label: 'Cooking' }, { value: 'CR', label: 'Crime' },
    { value: 'MY', label: 'Mystery' }, { value: 'SF', label: 'Science Fiction' },
    { value: 'FAN', label: 'Fantasy' }, { value: 'HIS', label: 'History' },
    { value: 'ROM', label: 'Romance' }, { value: 'TXT', label: 'Textbook' },
];

const bookConditions = [
    { value: 'NW', label: 'New' }, { value: 'GD', label: 'Good' },
    { value: 'FR', label: 'Fair' }, { value: 'PO', label: 'Poor' },
];

// <<< ADD: Helper to extract relative path from URL (similar to ProfilePage) >>>
const getRelativeImagePathFromUrl = (fullUrl: string | null | undefined): string | null => {
    if (!fullUrl || typeof fullUrl !== 'string') {
        return null;
    }
    // Find the part of the URL that corresponds to the relative path
    // Assumes structure like '.../static/images/filename.jpg' or '.../media/images/filename.jpg'
    const imageMarker = "/images/"; // Adjust if your structure is different (e.g., /covers/)
    const markerIndex = fullUrl.lastIndexOf(imageMarker);

    if (markerIndex !== -1) {
        // Extract the part starting from 'images/'
        return fullUrl.substring(markerIndex + 1); // e.g., "images/library_seal.jpg"
    }
    console.warn("Could not determine relative path from image URL:", fullUrl);
    return null;
};


const EditBookForm: React.FC<EditBookFormProps> = ({ book, onBookUpdated, onCancel }) => {
    const { getCSRFToken } = useAuth();

    // State for form fields
    const [title, setTitle] = useState(book.title || '');
    const [author, setAuthor] = useState(book.author || '');
    const [isbn, setIsbn] = useState(book.isbn || '');
    const [category, setCategory] = useState(book.category || '');
    const [language, setLanguage] = useState(book.language || '');
    const [condition, setCondition] = useState(book.condition || '');
    const [storageLocation, setStorageLocation] = useState(book.storage_location || '');
    const [publisher, setPublisher] = useState(book.publisher || '');
    const [publicationYear, setPublicationYear] = useState<string>(book.publication_year?.toString() || '');
    const [copyNumber, setCopyNumber] = useState<string>(book.copy_number?.toString() || '');
    // <<< CHANGE: State for image path (string to be sent to backend) >>>
    // Initialize with the relative path extracted from the book's image_url
    const [imagePath, setImagePath] = useState<string>(getRelativeImagePathFromUrl(book.image_url) || '');

    // Update state if the book prop changes
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
        // <<< CHANGE: Update imagePath state based on book.image_url >>>
        setImagePath(getRelativeImagePathFromUrl(book.image_url) || '');
    }, [book]);


    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Error: Could not verify security token. Please refresh and try again.");
            return;
        }

        // --- Prepare Payload ---
        // Use Partial<Book> or a more specific type for the payload
        const payload: { [key: string]: any } = {
            title,
            author,
            isbn,
            category,
            language,
            condition,
            storage_location: storageLocation || null,
            publisher: publisher || null,
            publication_year: publicationYear ? parseInt(publicationYear, 10) || null : null,
            copy_number: copyNumber ? parseInt(copyNumber, 10) || null : null,
            // <<< CHANGE: Send the imagePath string >>>
            // Send the current value of imagePath state. Backend expects relative path.
            image: imagePath || null, // Send null if empty string
        };

        // Basic validation
        if (publicationYear && isNaN(payload.publication_year as number)) {
            alert("Please enter a valid publication year."); return;
        }
        if (copyNumber && isNaN(payload.copy_number as number)) {
            alert("Please enter a valid copy number."); return;
        }

        try {
            const response = await fetch(`/api/books/${book.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(payload),
                credentials: 'include',
            });

            if (response.ok) {
                const updatedBookData: Book = await response.json();
                alert('Book updated successfully!');
                onBookUpdated(updatedBookData);
            } else {
                let errorMsg = 'Error updating book';
                try {
                    const errorData = await response.json();
                    if (typeof errorData === 'object' && errorData !== null) {
                        errorMsg = Object.entries(errorData)
                            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('\n');
                    } else if (errorData.detail) { errorMsg = errorData.detail; }
                } catch (e) { errorMsg = `Error updating book (Status: ${response.status})`; }
                alert(errorMsg);
            }
        } catch (error) {
            console.error('Error updating book:', error);
            alert('Failed to update book. Please check console for details.');
        }
    };

    return (
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
                {bookCategories.map((cat) => ( <option key={cat.value} value={cat.value}>{cat.label}</option> ))}
            </select>

            <label htmlFor="edit-language">Language:</label>
            <input type="text" id="edit-language" value={language} onChange={(e) => setLanguage(e.target.value)} required />

            <label htmlFor="edit-condition">Condition:</label>
            <select id="edit-condition" value={condition} onChange={(e) => setCondition(e.target.value)} required>
                {bookConditions.map((cond) => ( <option key={cond.value} value={cond.value}>{cond.label}</option> ))}
            </select>

            <label htmlFor="edit-storageLocation">Storage Location:</label>
            <input type="text" id="edit-storageLocation" value={storageLocation} onChange={(e) => setStorageLocation(e.target.value)} />

            <label htmlFor="edit-publisher">Publisher:</label>
            <input type="text" id="edit-publisher" value={publisher} onChange={(e) => setPublisher(e.target.value)} />

            <label htmlFor="edit-publicationYear">Publication Year:</label>
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="edit-publicationYear" value={publicationYear} onChange={(e) => setPublicationYear(e.target.value)} />

            <label htmlFor="edit-copyNumber">Copy Number:</label>
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="edit-copyNumber" value={copyNumber} onChange={(e) => setCopyNumber(e.target.value)} />

            {/* <<< CHANGE: Input for image path (relative path expected by backend) >>> */}
            <label htmlFor="edit-imagePath">Image Path (e.g., images/covers/new.jpg):</label>
            <input
                type="text"
                id="edit-imagePath"
                value={imagePath}
                onChange={(e) => setImagePath(e.target.value)}
                placeholder="Relative path from static/media root"
            />
            {/* Display current image for reference */}
            {book.image_url && <img src={book.image_url} alt="Current cover" style={{maxWidth: '100px', marginTop: '5px'}}/>}


            <div className="edit-form-buttons">
                <button type="submit">Update Book</button>
                <button type="button" onClick={onCancel} className="cancel-button">Cancel</button>
            </div>
        </form>
    );
};

export default EditBookForm;