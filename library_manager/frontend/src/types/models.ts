// Central type definitions for backend models

// Corresponds to backend UserProfileSerializer
export interface UserProfile {
    user_id: number;
    username: string;
    type: 'AD' | 'US' | 'LB'; // Use literal types for known choices
    age: number | null;
    avatar_url: string | null; // Expect the full URL from backend
    get_type_display: string;
}

// Corresponds to backend UserSerializer
export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    profile: UserProfile | null; // Profile can be null
    date_joined: string; // ISO date string
    is_staff: boolean;
}

// Corresponds to backend BookSerializer
export interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    category: string; // e.g., 'CK', 'SF'
    category_display: string; // Human-readable category (Assuming backend always provides it)
    language: string;
    condition: string; // e.g., 'NW', 'GD'
    condition_display: string; // Human-readable condition (Assuming backend always provides it)
    available: boolean;
    image_url: string | null; // Full URL or null
    borrower: string | null; // Username
    borrower_id: number | null;
    borrow_date: string | null; // ISO date string
    due_date: string | null; // ISO date string
    storage_location: string | null;
    publisher: string | null;
    publication_year: number | null;
    copy_number: number | null;
    added_by: string | null; // Username
    added_by_id: number | null;
    // Derived fields from serializer
    days_left: number | null;
    overdue: boolean;
    days_overdue: number | null;
    due_today: boolean;
}

// Interface for Paginated API responses (like for books)
export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}