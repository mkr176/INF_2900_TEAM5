import os
import django
import sys
import datetime
import json # Added import for json

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
        with open(file_path, 'r') as f:
            books_data = json.load(f)
        return books_data
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure the file exists.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Please check the file format.")
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
        user, created = People.objects.update_or_create(
            email=user_data["email"], defaults=user_data
        )
        users.append(user)

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
        user2, created = User.objects.update_or_create(
            username=user2_data["username"],
            defaults={
                "password": user2_data[
                    "password"
                ],  # password needs to be handled separately
                "email": user2_data["email"],
                "first_name": user2_data["first_name"],
                "last_name": user2_data["last_name"],
            },
        )
        if created:  # if user was created, set the password
            user2.set_password(user2_data["password"])
            user2.save()
        users2.append(user2)

    books_data = load_books_from_json() # Load books data from json file

    books = []
    for book_data in books_data:
        book, created = Book.objects.update_or_create(
            isbn=book_data["isbn"], defaults=book_data
        )
        books.append(book)

    print("initialized correctly!")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print("An error occurred: ", e)