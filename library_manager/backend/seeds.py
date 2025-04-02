import os
import django
import sys
import datetime
import json # Added import for json

# --- Start of modifications ---
# Ensure the project root directory (library_manager) is in the Python path
# This helps resolve imports correctly, especially when running seeds.py directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)
# --- End of modifications ---

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from backend.models import People, Book
from django.db import connection
import datetime

from django.contrib.auth.models import User

with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    print("Database connected successfully!")

def load_books_from_json(): # Added function to load books from json
    file_path = os.path.join(os.path.dirname(__file__), 'books_data.json') # Construct file path
    try:
        with open(file_path, 'r', encoding='utf-8') as f: # Specify UTF-8 encoding
            books_data = json.load(f)
        return books_data
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure the file exists.")
        return []
    except json.JSONDecodeError as e: # Add more detail to JSON error
        print(f"Error: Could not decode JSON from {file_path}. Please check the file format. Details: {e}")
        return []


def seed_database():
    # Crear usuarios
    users_data = [
        {
            "name": "Admin User",
            "numberbooks": 0,
            "type": "AD",
            "age": 30,
            "email": "a@gmail.com",
            "password": "admin123",
        },
        {
            "name": "Regular User",
            "numberbooks": 2,
            "type": "US",
            "age": 25,
            "email": "b@gmail.com",
            "password": "user123",
        },
        {
            "name": "Librarian User",
            "numberbooks": 5,
            "type": "LB",
            "age": 35,
            "email": "c@gmail.com",
            "password": "librarian123",
        },
    ]

    users = []
    for user_data in users_data:
        # Use update_or_create for People model as well
        person, created = People.objects.update_or_create(
            email=user_data["email"],
            defaults={
                "name": user_data["name"],
                "numberbooks": user_data["numberbooks"],
                "type": user_data["type"],
                "age": user_data["age"],
                "password": user_data["password"], # Storing plain text password here is not ideal, but matches existing code
            }
        )
        users.append(person)
        if created:
            print(f"Created People: {person.name}")
        else:
            print(f"Updated People: {person.name}")


    # Crear usuarios User (Django Auth User)
    users2_data = [
        {
            "username": "AdminUser",
            "password": "admin123",
            "email": "a@gmail.com",
            "first_name": "Admin",
            "last_name": "User",
        },
        {
            "username": "RegularUser",
            "password": "user123",
            "email": "b@gmail.com",
            "first_name": "Regular",
            "last_name": "User",
        },
        {
            "username": "LibrarianUser",
            "password": "librarian123",
            "email": "c@gmail.com",
            "first_name": "Librarian",
            "last_name": "User",
        },
    ]

    users2 = []
    for user2_data in users2_data:
        # Check if user exists before creating/updating
        user_exists = User.objects.filter(username=user2_data["username"]).exists()
        user2, created = User.objects.update_or_create(
            username=user2_data["username"],
            defaults={
                # Don't update password in defaults if user exists, handle below
                "email": user2_data["email"],
                "first_name": user2_data["first_name"],
                "last_name": user2_data["last_name"],
            },
        )
        # Always set/update the password using set_password for hashing
        user2.set_password(user2_data["password"])
        user2.save()
        users2.append(user2)
        if created:
            print(f"Created Auth User: {user2.username}")
        elif not user_exists:
             print(f"Created Auth User (via update_or_create defaults): {user2.username}")
        else:
            print(f"Updated Auth User: {user2.username}")


    books_data = load_books_from_json() # Load books data from json file

    if not books_data:
        print("No book data loaded, skipping book seeding.")
        return # Exit if no books were loaded

    books = []
    for book_data in books_data:
        # --- Modification: Handle potential missing keys gracefully ---
        defaults = {
            "title": book_data.get("title", "Unknown Title"),
            "author": book_data.get("author", "Unknown Author"),
            "due_date": book_data.get("due_date"), # Keep null if not present
            "category": book_data.get("category", "TXT"), # Default category if missing
            "language": book_data.get("language", "English"),
            # user field is intentionally left out, should be set on borrow
            "condition": book_data.get("condition", "GD"), # Default condition
            "available": book_data.get("available", True),
            # --- Modification: Ensure image path is correctly handled ---
            # Store the relative path as defined in JSON. Serving is handled by staticfiles.
            "image": book_data.get("image", 'static/images/library_seal.jpg'), # Use default if missing
            "storage_location": book_data.get("storage_location"),
            "publisher": book_data.get("publisher"),
            "publication_year": book_data.get("publication_year"),
            "copy_number": book_data.get("copy_number", 1), # Default copy number
            # --- Modification: Ensure borrower and borrow_date are null initially ---
            "borrower": None,
            "borrow_date": None,
        }
        # --- End of Modifications ---

        # Ensure ISBN exists before trying to create/update
        isbn = book_data.get("isbn")
        if not isbn:
            print(f"Skipping book due to missing ISBN: {book_data.get('title', 'N/A')}")
            continue

        try:
            book, created = Book.objects.update_or_create(
                isbn=isbn, defaults=defaults
            )
            books.append(book)
            if created:
                print(f"Created Book: {book.title}")
            else:
                print(f"Updated Book: {book.title}")
        except Exception as e:
            print(f"Error creating/updating book with ISBN {isbn}: {e}")
            print(f"Data causing error: {book_data}")


    print("Database seeding process completed!")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print("An error occurred during seeding: ", e)