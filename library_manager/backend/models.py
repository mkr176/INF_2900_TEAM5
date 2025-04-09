from django.db import models
from django.conf import settings # Import settings to reference the AUTH_USER_MODEL

# Removed the old People model

# Renamed People to UserProfile and linked it to the standard User model
class UserProfile(models.Model):
    TYPES = [
        ('AD','Admin'),
        ('US','User'),
        ('LB','Librarian')
    ]
    # Link to the built-in User model (or custom user model defined in settings)
    # primary_key=True makes this the primary key for the profile table
    # related_name='profile' allows accessing profile via user.profile
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If the User is deleted, delete the profile too
        primary_key=True,
        related_name='profile'
    )
    # Keep the type field to distinguish roles
    type = models.CharField(max_length=10, choices=TYPES, default='US') # Default to 'User'
    # Age can be optional
    age = models.IntegerField(null=True, blank=True)
    # Add an avatar field (optional)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.svg', null=True, blank=True)

    # Removed name, email, password, numberbooks (handled by User model or derived)

    def __str__(self):
        # Use the related user's username for representation
        return f"{self.user.username}'s Profile ({self.get_type_display()})"

class Book(models.Model):
    CATEGORIES = [
        ('CK', 'Cooking'),
        ('CR', 'Crime'),
        ('MY', 'Mistery'), # Typo: Should be 'Mystery'
        ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'),
        ('HIS', 'History'),
        ('ROM', 'Romance'),
        ('TXT', 'Textbook'),
    ]
    CONDITIONS = [
        ('NW','New'),
        ('GD','Good'),
        ('FR','Fair'),
        ('PO','Poor')
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=3, choices=CATEGORIES)
    language = models.CharField(max_length=50)

    # Changed ForeignKey to point to AUTH_USER_MODEL. Represents who added the book.
    # Renamed related_name for clarity. SET_NULL keeps the book if the user is deleted.
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_books' # User.added_books gives books added by this user
    )
    condition = models.CharField(max_length=4, choices=CONDITIONS)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', default='static/images/library_seal.jpg')
    
    # Changed ForeignKey to point to AUTH_USER_MODEL. Represents who borrowed the book.
    # Renamed related_name for clarity. SET_NULL keeps the book, clears borrower if user deleted.
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_books' # User.borrowed_books gives books borrowed by this user
    )
    borrow_date = models.DateField(null=True, blank=True)
    storage_location = models.CharField(max_length=200, blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    copy_number = models.IntegerField(blank=True, null=True)

    # Removed the old 'user' field which pointed to People

    def __str__(self):
        return self.title


