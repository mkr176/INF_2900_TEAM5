import os
import django
import sys
import datetime
import json

# --- Path Setup ---
# Calculate the project root directory (the parent of 'backend')
# __file__ is the path to seeds.py (e.g., C:/.../library_manager/backend/seeds.py)
# os.path.dirname(__file__) is the 'backend' directory
# os.path.join(..., '..') goes one level up to 'library_manager'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root directory to sys.path BEFORE trying to import 'backend'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT) # Insert at the beginning for precedence

# Set the DJANGO_SETTINGS_MODULE environment variable
# It should point to the settings file relative to a directory in sys.path
# Since PROJECT_ROOT is in sys.path, 'backend.settings' is correct.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Setup Django environment
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}.")
    print(f"PROJECT_ROOT added to sys.path: {PROJECT_ROOT}")
    print(f"sys.path: {sys.path}")
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    sys.exit(1)


# --- Model Imports ---
# Use relative import because seeds.py is in the same directory as models.py
try:
    from backend.models import UserProfile, Book # <<< REVERTED TO ABSOLUTE IMPORT
    from django.contrib.auth import get_user_model
except ModuleNotFoundError:
    print("Error: Could not find the 'backend' module.")
    print(f"Is the project root ({PROJECT_ROOT}) correctly added to sys.path?")
    print(f"sys.path: {sys.path}")
    sys.exit(1)
except ImportError as e:
    print(f"Error importing models: {e}")
    print("Ensure seeds.py is in the 'backend' directory alongside models.py and __init__.py exists.")
    sys.exit(1)

from django.db import connection
from django.core.files.base import ContentFile # For handling default image if needed

User = get_user_model() # Get the active User model

# --- Database Connection Check ---
try:
    with connection.cursor() as cursor:
        # Try a simple query to ensure connection
        cursor.execute("SELECT 1")
        print("Database connected successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")
    sys.exit(1) # Exit if DB connection fails

# --- Data Loading Function ---
def load_books_from_json():
    """Loads book data from a JSON file."""
    file_path = os.path.join(os.path.dirname(__file__), 'books_data.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f: # Specify UTF-8 encoding
            books_data = json.load(f)
        print(f"Successfully loaded {len(books_data)} books from {file_path}")
        return books_data
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure the file exists.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {file_path}. Check format. Details: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred loading books: {e}")
        return []

# --- Seeding Function ---
def seed_database():
    """Populates the database with initial User, UserProfile, and Book data."""
    print("Starting database seeding...")

    # --- 1. Seed Users and UserProfiles ---
    # Combined user data structure
    users_data = [
        {
            "username": "AdminUser", "password": "admin123", "email": "admin@example.com",
            "first_name": "Admin", "last_name": "User", "profile_type": "AD", "profile_age": 30
        },
        {
            "username": "RegularUser", "password": "user123", "email": "user@example.com",
            "first_name": "Regular", "last_name": "User", "profile_type": "US", "profile_age": 25
        },
        {
            "username": "LibrarianUser", "password": "librarian123", "email": "librarian@example.com",
            "first_name": "Librarian", "last_name": "User", "profile_type": "LB", "profile_age": 35
        },
    ]

    created_users = {} # Store created users if needed later (e.g., for added_by)

    print("\n--- Seeding Users and Profiles ---")
    for user_data in users_data:
        profile_type = user_data.pop("profile_type", "US") # Default to 'US' if missing
        profile_age = user_data.pop("profile_age", None)
        password = user_data.pop("password") # Extract password, don't store in defaults

        try:
            user, created = User.objects.update_or_create(
                username=user_data["username"],
                defaults=user_data # Pass remaining data as defaults
            )

            # Always set/update the password correctly
            user.set_password(password)
            user.save()

            if created:
                print(f"Created User: {user.username}")
            else:
                print(f"Updated User: {user.username}")

            created_users[user.username] = user # Store user instance

            # Create or update the associated UserProfile
            profile, profile_created = UserProfile.objects.update_or_create(
                user=user,
                defaults={'type': profile_type, 'age': profile_age}
            )

            if profile_created:
                print(f"  - Created Profile for {user.username} (Type: {profile.get_type_display()})")
            else:
                print(f"  - Updated Profile for {user.username} (Type: {profile.get_type_display()})")

        except Exception as e:
            print(f"Error creating/updating user {user_data.get('username', 'N/A')}: {e}")


    # --- 2. Seed Books ---
    print("\n--- Seeding Books ---")
    books_data = load_books_from_json()

    if not books_data:
        print("No book data loaded or found. Skipping book seeding.")
    else:
        # Optional: Get an admin user to set as 'added_by'
        admin_user = created_users.get("AdminUser", None)
        if not admin_user:
            print("Warning: AdminUser not found. 'added_by' for books will be set to None.")

        for book_data in books_data:
            isbn = book_data.get("isbn")
            if not isbn:
                print(f"Skipping book due to missing ISBN: {book_data.get('title', 'N/A')}")
                continue

            # Prepare defaults dictionary matching the Book model fields
            defaults = {
                "title": book_data.get("title", "Unknown Title"),
                "author": book_data.get("author", "Unknown Author"),
                "category": book_data.get("category", "TXT"), # Default category
                "language": book_data.get("language", "English"),
                "condition": book_data.get("condition", "GD"), # Default condition
                "available": book_data.get("available", True),
                "storage_location": book_data.get("storage_location"),
                "publisher": book_data.get("publisher"),
                "publication_year": book_data.get("publication_year"),
                "copy_number": book_data.get("copy_number", 1),
                # --- Foreign Keys and Dates ---
                "added_by": admin_user, # Set to the admin user found earlier, or None
                "borrower": None,       # Initially not borrowed
                "borrow_date": None,    # Initially no borrow date
                "due_date": None,       # Initially no due date
                # --- Image Handling ---
                # Use the path from JSON or a default. Assumes MEDIA_ROOT/STATIC_ROOT setup.
                "image": book_data.get("image", 'images/library_seal.jpg'), # Relative path
            }

            try:
                book, created = Book.objects.update_or_create(
                    isbn=isbn, defaults=defaults
                )
                if created:
                    print(f"Created Book: {book.title} (ISBN: {book.isbn})")
                else:
                    print(f"Updated Book: {book.title} (ISBN: {book.isbn})")

                # --- Handle potential image file creation if default is used and doesn't exist ---
                # This part is complex and depends on storage backend.
                # For simplicity, we assume the default image file exists where Django expects it.
                # If 'image' field requires an actual file upload during seeding,
                # you might need to use ContentFile and save() explicitly.
                # Example (if needed):
                # if created and not book.image: # If newly created and image is default/missing
                #    try:
                #        # Assuming default image is accessible
                #        default_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images/library_seal.jpg') # Adjust path as needed
                #        if os.path.exists(default_image_path):
                #            with open(default_image_path, 'rb') as f:
                #                book.image.save('library_seal.jpg', ContentFile(f.read()), save=True)
                #        else:
                #             print(f"Warning: Default image not found at {default_image_path}")
                #    except Exception as img_err:
                #        print(f"Warning: Could not set default image for {book.title}: {img_err}")


            except Exception as e:
                print(f"Error creating/updating book with ISBN {isbn}: {e}")
                # Optionally print the data causing the error for debugging:
                # print(f"Data causing error: {book_data}")
                # print(f"Defaults used: {defaults}")


    print("\nDatabase seeding process completed!")


# --- Main Execution Block ---
if __name__ == "__main__":
    # This block executes when run directly, e.g., `python backend/seeds.py`
    print(f"Running seeds.py directly from: {os.getcwd()}")
    print(f"PROJECT_ROOT added to sys.path: {PROJECT_ROOT}")
    # print(f"Full sys.path: {sys.path}") # Uncomment for detailed debugging if needed
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

    try:
        seed_database()
    except Exception as e:
        print(f"\nAn critical error occurred during the seeding process: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging