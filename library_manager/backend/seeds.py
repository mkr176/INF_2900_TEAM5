import os
import django
import sys
import datetime

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

    books_data = [
        {
            "title": "Banda Municipal de Sangüesa",
            "author": "Juan Cruz Labeaga Mendiola",
            "due_date": datetime.date(2025, 6, 1),
            "isbn": "84-87120-27-X",
            "category": "HIS",
            "language": "Spanish",
            "user": users[1],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf D4",
            "publisher": "Gobierno de Navarra",
            "publication_year": 1990,
            "copy_number": 1,
        },
        {
            "title": "Hygge for Hardangerfjord Hikers: A Koselig Guide to Conquering Cliffs",
            "author": "Astrid Fjord",
            "due_date": datetime.date(2025, 7, 1),
            "isbn": "9781234567001",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[0],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf N1",
            "publisher": "Cozy Trails Publishing",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "The Introvert's Guide to Oslo Nightlife (and Why You Should Stay Home)",
            "author": "Bjørn Stillenatt",
            "due_date": datetime.date(2025, 8, 1),
            "isbn": "9781234567002",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf I2",
            "publisher": "Quiet Nights Press",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "50 Shades of Brunost: A Cheesy Love Story",
            "author": "Greta Geitost",
            "due_date": datetime.date(2025, 9, 1),
            "isbn": "9781234567003",
            "category": "ROM",
            "language": "English",  # ROM - Romance
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf C5",
            "publisher": "Dairy Tales Publishing",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "Silence of the Fjords: A Thrillingly Quiet Mystery",
            "author": "Lars Lydløs",
            "due_date": datetime.date(2025, 10, 1),
            "isbn": "9781234567004",
            "category": "MY",
            "language": "English",  # MY - Mystery
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf M7",
            "publisher": "Silent Peaks Mysteries",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "Knit Your Own Viking Helmet: A Cozy Crafting Adventure",
            "author": "Solveig Ulltråd",
            "due_date": datetime.date(2025, 11, 1),
            "isbn": "9781234567005",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf K9",
            "publisher": "Woolly Warrior Crafts",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "The Little Book of Lagom... Just Kidding, Go Big or Go Home (Norwegian Edition)",
            "author": "Magnus Maksimal",
            "due_date": datetime.date(2025, 12, 1),
            "isbn": "9781234567006",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf L1",
            "publisher": "Janteloven Jokes Inc.",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "My Summer Vacation in a Hytte (and I Only Saw the Sun Twice)",
            "author": "Ingrid Regnvær",
            "due_date": datetime.date(2026, 1, 1),
            "isbn": "9781234567007",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf H3",
            "publisher": "Rainy Day Reads",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "Left Out in the Cold: A Guide to Norwegian Socializing (or Lack Thereof)",
            "author": "Frode Frys",
            "due_date": datetime.date(2026, 2, 1),
            "isbn": "9781234567008",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf J4",
            "publisher": "Awkward Penguin Press",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "The Joy of Janteloven: Why Being Average is Actually Awesome",
            "author": "Kari Beskjeden",
            "due_date": datetime.date(2026, 3, 1),
            "isbn": "9781234567009",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf B6",
            "publisher": "Modesty Matters Media",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "From Fjord to Fork: The Ultimate Lutefisk Cookbook",
            "author": "Sven Fiskesuppe",
            "due_date": datetime.date(2026, 4, 1),
            "isbn": "9781234567010",
            "category": "CK",
            "language": "English",  # CK - Cooking
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf F8",
            "publisher": "Lutefisk Lovers Ltd.",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "The Norwegian Guide to Avoiding Eye Contact: A Masterclass",
            "author": "Hilda Blikkstille",
            "due_date": datetime.date(2026, 5, 1),
            "isbn": "9781234567011",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf D10",
            "publisher": "Shifty Eyes Publications",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "Vikings on Vespas: Modern Myths of Norway",
            "author": "Ragnar Moderne",
            "due_date": datetime.date(2026, 6, 1),
            "isbn": "9781234567012",
            "category": "HIS",
            "language": "English",  # HIS - History
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf G1",
            "publisher": "Anachronistic Adventures",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "Koselig Crime Scenes: A Detective in a Wool Sweater Mystery",
            "author": "Eva Varm",
            "due_date": datetime.date(2026, 7, 1),
            "isbn": "9781234567013",
            "category": "MY",
            "language": "English",  # MY - Mystery
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf E3",
            "publisher": "Cozy Crime Co.",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "The Unofficial Guide to Surviving a Norwegian Winter (Without Going Mad)",
            "author": "Ole Mørketid",
            "due_date": datetime.date(2026, 8, 1),
            "isbn": "9781234567014",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf A5",
            "publisher": "Polar Night Press",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "Speak Like a Viking: A Phrasebook for the Modern Norwegian",
            "author": "Torvald Gammelord",
            "due_date": datetime.date(2026, 9, 1),
            "isbn": "9781234567015",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf C7",
            "publisher": "Ancient Tongues Today",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "The Art of the Norwegian Stare: Communication Without Words",
            "author": "Liv Stillhet",
            "due_date": datetime.date(2026, 10, 1),
            "isbn": "9781234567016",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf I9",
            "publisher": "Silent Signals Society",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "My 1000-Hour Hike: A Norwegian Nature Memoir (in Real Time)",
            "author": "Jens Langtur",
            "due_date": datetime.date(2026, 11, 1),
            "isbn": "9781234567017",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf L2",
            "publisher": "Endurance Explorers",
            "publication_year": 2023,
            "copy_number": 1,
        },
        {
            "title": "The Hygge Hypothesis: Is 'Kos' Just an Excuse for Staying Indoors?",
            "author": "Professor Koskritisk",
            "due_date": datetime.date(2026, 12, 1),
            "isbn": "9781234567018",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[2],
            "condition": "NW",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf H4",
            "publisher": "Kos Konundrums Press",
            "publication_year": 2024,
            "copy_number": 1,
        },
        {
            "title": "Norwegian Minimalism: Owning Only What Fits in Your Backpack (for Hiking)",
            "author": "Milla Minimalist",
            "due_date": datetime.date(2027, 1, 1),
            "isbn": "9781234567019",
            "category": "TXT",
            "language": "English",  # TXT - Textbook/Guidebook
            "user": users[0],
            "condition": "FR",
            "available": False,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf J6",
            "publisher": "Less is More Mountains",
            "publication_year": 2022,
            "copy_number": 1,
        },
        {
            "title": "Help, I Married a Norwegian! A Humorous Handbook for Husbands/Wives",
            "author": "Ulf Gift",
            "due_date": datetime.date(2027, 2, 1),
            "isbn": "9781234567020",
            "category": "ROM",
            "language": "English",  # ROM - Romance
            "user": users[1],
            "condition": "GD",
            "available": True,
            "image": "static/images/library_seal.jpg",
            "storage_location": "Shelf B8",
            "publisher": "Cultural Clash Comedy",
            "publication_year": 2023,
            "copy_number": 1,
        },
    ]

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
