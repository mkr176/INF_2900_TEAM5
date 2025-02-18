import os
import django
import sys
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from frontend.models import User, Libro
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    print("Database connected successfully!")


def seed_database():
    # Crear usuarios
    users = [
        User.objects.create(name="Admin User", numberbooks=0, type='AD'),
        User.objects.create(name="Regular User", numberbooks=2, type='US'),
        User.objects.create(name="Librarian User", numberbooks=5, type='LB'),
    ]

    # Crear libros
    books = [
        Libro.objects.create(
            title="Cooking Book", author="Author 1", due_date=datetime.date(2025, 3, 1),
            isbn="1234567890123", category='CK', language="English", 
            user=users[1], condition='NW', available=True
        ),
        Libro.objects.create(
            title="Crime Book", author="Author 2", due_date=datetime.date(2025, 4, 1),
            isbn="1234567890124", category='CR', language="English", 
            user=users[2], condition='GD', available=True
        ),
        Libro.objects.create(
            title="Mistery Book", author="Author 3", due_date=datetime.date(2025, 5, 1),
            isbn="1234567890125", category='MY', language="English",
            user=users[0], condition='FR', available=False
        ),
    ]

    print("Base de datos inicializada correctamente!")

if __name__ == "__main__":
    seed_database()
