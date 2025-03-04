import os
import django
import sys
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from backend.models import User, Book
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    print("Database connected successfully!")


def seed_database():
    # Crear usuarios
    User.objects.all().delete()
    Book.objects.all().delete()
    users = [
        User.objects.create(name="Admin User", numberbooks=0, type='AD', age=30, email="a@gmail.com", password="admin123"),
        User.objects.create(name="Regular User", numberbooks=2, type='US', age=25, email="b@gmail.com", password="user123"),
        User.objects.create(name="Librarian User", numberbooks=5, type='LB', age=35, email="c@gmail.com", password="librarian123"),
    ]

    # Crear libros
    books = [
        Book.objects.create(
            title="Cooking Book", author="Author 1", due_date=datetime.date(2025, 3, 1),
            isbn="1234567890123", category='CK', language="English", 
            user=users[1], condition='NW', available=True, image='images/library_seal.jpg'
        ),
        Book.objects.create(
            title="Crime Book", author="Author 2", due_date=datetime.date(2025, 4, 1),
            isbn="1234567890124", category='CR', language="English", 
            user=users[2], condition='GD', available=True, image='images/library_seal.jpg'
        ),
        Book.objects.create(
            title="Mistery Book", author="Author 3", due_date=datetime.date(2025, 5, 1),
            isbn="1234567890125", category='MY', language="English",
            user=users[0], condition='FR', available=False, image='images/library_seal.jpg'
        ),
        Book.objects.create(
            title="Banda Municipal de Sangüesa", author="Juan Cruz Labeaga Mendiola", due_date=datetime.date(2025, 6, 1),
            isbn="84-87120-27-X", category='HIS', language="Spanish",
            user=users[1], condition='NW', available=True, image='images/library_seal.jpg'
        )
    ]

    print("initialized correctly!")

if __name__ == "__main__":
    seed_database()
