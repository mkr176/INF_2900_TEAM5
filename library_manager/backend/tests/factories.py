# Example structure - details to be filled in
import factory
from django.contrib.auth import get_user_model
from backend import models # Use absolute import based on project structure

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',) # Avoid creating duplicate users in tests

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    # Use post-generation hook for password to ensure hashing
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or 'defaultpassword' # Use provided password or a default
        self.set_password(password)
        if create:
            self.save() # Save again after setting password if needed

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserProfile

    user = factory.SubFactory(UserFactory) # Automatically create a related User
    type = 'US' # Default type
    age = factory.Faker("random_int", min=18, max=90)
    # avatar = ... # Handle image field if needed, often omitted in basic factories

class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book
        django_get_or_create = ('isbn',) # Avoid duplicate books

    title = factory.Sequence(lambda n: f"Test Book Title {n}")
    author = factory.Faker("name")
    isbn = factory.Sequence(lambda n: f"9780000000{n:03d}") # Generate unique ISBNs
    category = factory.Iterator(models.Book.CATEGORIES, getter=lambda c: c[0]) # Cycle through categories
    language = "English"
    condition = factory.Iterator(models.Book.CONDITIONS, getter=lambda c: c[0]) # Cycle through conditions
    available = True
    publisher = factory.Faker("company")
    publication_year = factory.Faker("year")

    # Set added_by using a SubFactory or pass it during creation
    # added_by = factory.SubFactory(UserFactory) # Example if needed

    # borrower = None # Default
    # borrow_date = None # Default
    # due_date = None # Default