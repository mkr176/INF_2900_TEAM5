import React, { useState } from 'react'; // Removed useEffect as CSRF is handled by context
import { useAuth } from '../../context/AuthContext'; // Import useAuth to get CSRF token
import "./AddBookForm.css";

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
    const [condition, setCondition] = useState(bookConditions[1].value); // Default to 'Good'
    const [storageLocation, setStorageLocation] = useState('Shelf A1'); // Default value
    const [publisher, setPublisher] = useState('Tromsø University Press');
    const [publicationYear, setPublicationYear] = useState<number | string>(''); // Allow number or string for input, send number
    const [copyNumber, setCopyNumber] = useState<number | string>(1); // Default to 1, send number
    // 'available' state is removed as it's read-only in the serializer for creation

    const { getCSRFToken } = useAuth(); // Get CSRF token function from context

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        // --- Get CSRF Token ---
        const csrfToken = await getCSRFToken();
        if (!csrfToken) {
            alert("Error: Could not verify security token. Please refresh and try again.");
            return;
        }
        // --- End CSRF Token ---

        // Convert year and copy number to numbers, handle potential errors
        const year = publicationYear ? parseInt(String(publicationYear), 10) : null;
        const copyNum = copyNumber ? parseInt(String(copyNumber), 10) : null;

        if (publicationYear && isNaN(year as number)) {
            alert("Please enter a valid publication year.");
            return;
        }
        if (copyNumber && isNaN(copyNum as number)) {
            alert("Please enter a valid copy number.");
            return;
        }

        const bookData = {
            title,
            author,
            isbn,
            category,
            language,
            condition,
            // available is not sent, defaults to True on backend
            storage_location: storageLocation || null, // Send null if empty
            publisher: publisher || null, // Send null if empty
            publication_year: year, // Send parsed number or null
            copy_number: copyNum, // Send parsed number or null
            // added_by is set automatically by the backend
            // borrower, borrow_date, due_date are not relevant for creation
        };

        try {
            // <<< CHANGE: Update API endpoint >>>
            const response = await fetch('/api/books/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // <<< CHANGE: Include CSRF token >>>
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(bookData),
                credentials: 'include', // Include cookies for session auth
            });

            if (response.ok) {
                alert('Book created successfully!');
                // Reset form fields after successful submission
                setTitle('');
                setAuthor('');
                setIsbn('');
                setCategory(bookCategories[0].value);
                setLanguage('English');
                setCondition(bookConditions[1].value);
                setStorageLocation('');
                setPublisher('');
                setPublicationYear('');
                setCopyNumber(1);
                if (onBookCreated) {
                    onBookCreated(); // Notify parent component about book creation
                }
            } else {
                // <<< CHANGE: Improved error handling >>>
                let errorMsg = 'Error creating book';
                try {
                const errorData = await response.json();
                    // Flatten potential nested errors
                    if (typeof errorData === 'object' && errorData !== null) {
                        errorMsg = Object.entries(errorData)
                            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('\n');
                    } else if (errorData.detail) { // DRF often uses 'detail' for general errors
                         errorMsg = errorData.detail;
                    }
                } catch(e) {
                    errorMsg = `Error creating book (Status: ${response.status})`;
                }
                alert(errorMsg);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create book. Please check console for details.');
        }
    };

    return (
        
        <form onSubmit={handleSubmit} className='form-container'>
            <div className='add-book-form'>
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
            {/* <<< CHANGE: Use text input for year for flexibility, parse in handler >>> */}
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="publicationYear" value={publicationYear} onChange={(e) => setPublicationYear(e.target.value)} />

            <label htmlFor="copyNumber">Copy Number:</label>
            {/* <<< CHANGE: Use text input for copy number, parse in handler >>> */}
            <input type="text" inputMode="numeric" pattern="[0-9]*" id="copyNumber" value={copyNumber} onChange={(e) => setCopyNumber(e.target.value)} />

            {/* Removed 'Available' checkbox as it's not sent during creation */}
            </div>
            <button type="submit" className='add-book-button'> ✔ </button>
        </form>
    );
};

export default AddBookForm;