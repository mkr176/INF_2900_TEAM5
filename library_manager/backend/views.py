import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView # <-- ADD THIS LINE
from django.contrib.auth.models import User as AuthUser # Alias Django's User model to avoid confusion
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model # Ensure this is imported

from rest_framework import generics
from datetime import datetime, timedelta
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

from .serializers import PeopleSerializer
from .validations import validate_username, validate_password, validate_email, validate_birth_date
from .models import Book,People


import re
MIN_PASSWORD_LENGTH = 6
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
AuthUser = get_user_model() # Use Django's configured user model

# Define the borrow limit constant
MAX_BORROW_LIMIT = 3


# Landing Page View
def front(request, *args, **kwargs):
    return render(request, 'startpage.html')  # Changed template name


class FrontendAppView(TemplateView):
    template_name = "frontend/index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ============================== #
# 1️ AUTHENTICATION ROUTES        #
# ============================== #

# Register View
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            birth_date_str = data.get('birthDate', '') # Get birthDate as string

            birth_date = None # Initialize birth_date to None
            if birth_date_str: # Only try to parse if birth_date_str is not empty
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            else:
                birth_date = datetime.now().date() # Or handle empty date as needed, e.g., set to today's date

            today=datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Check if user already exists - use Django's AuthUser here
            if AuthUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create user - use Django's AuthUser here
            AuthUser.objects.create_user(username=username, password=password, email=email)
            People.objects.create(name=username, numberbooks=0, type='US', age=25, email=email, password=password)

            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError as e: # Catch datetime parsing errors
            return JsonResponse({'error': str(e)}, status=400)
        

# Login View
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

@method_decorator(login_required, name="dispatch")
class BorrowedBooksView(View):
    def get(self, request):
        user = request.user
        people_user = People.objects.get(name=user.username)
        is_librarian_or_admin = people_user.type in ["LB", "AD"]
        today = date.today()

        if is_librarian_or_admin:
            borrowed_books = Book.objects.filter(available=False).select_related('borrower')
        else:
            borrowed_books = Book.objects.filter(available=False, borrower=people_user).select_related('borrower')

        borrowed_books_data = {}
        for book in borrowed_books:
            borrower_name = book.borrower.name if book.borrower else "Unknown"
            if borrower_name not in borrowed_books_data:
                borrowed_books_data[borrower_name] = []

            days_left = (book.due_date - today).days
            overdue = days_left < 0
            days_overdue = abs(days_left) if overdue else 0
            due_today = days_left == 0

            book_info = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "category": book.category,
                "language": book.language,
                "condition": book.condition,
                "image": str(book.image),
                "due_date": book.due_date.isoformat(),
                "borrower_id": book.borrower.id if book.borrower else None,
                "days_left": days_left,
                "overdue": overdue,
                "days_overdue": days_overdue,
                "due_today": due_today,
            }
            borrowed_books_data[borrower_name].append(book_info)

        # Convert the dictionary to a list of user groups for frontend
        grouped_borrowed_books = []
        for borrower_name, books in borrowed_books_data.items():
            grouped_borrowed_books.append({
                "borrower_name": borrower_name,
                "books": books
            })


        return JsonResponse({"borrowed_books_by_user": grouped_borrowed_books},  status=200)


# Logout View
@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request):
        logout(request)  # Clears session
        return JsonResponse({"message": "Logged out successfully"}, status=200)


# ============================== #
# 2️ USER MANAGEMENT ROUTES       #
# ============================== #



@method_decorator(login_required, name='dispatch')
class CurrentUserView(View):
    def get(self, request):
        user = request.user
        try:
            people = People.objects.get(name=user.username)
            user_data = {
                'id': user.id,
                'username': user.username,
                'type': people.type
            }
        except People.DoesNotExist:
            # ✅ Return user details even if "People" entry is missing
            user_data = {
                'id': user.id,
                'username': user.username,
                'type': "Unknown"
            }

        return JsonResponse(user_data)
    

@login_required
def get_user_info(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "username": request.user.username,
            "email": request.user.email,
        })
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    


# Create user view
@method_decorator(csrf_exempt, name='dispatch')
class CreateUserView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            age = data.get('age')
            email= data.get('email')
            password = data.get('password')
            numberbooks = 0
            type = data.get('type')
            # Validate fields
            if not name or not type:
                return JsonResponse({'error': 'All fields are required'}, status=400)
            # --- Potential Simplification Suggestion ---
            # The validation functions (validate_username, validate_password, validate_email)
            # seem designed for the registration form (checking AuthUser, password complexity).
            # Using them here for creating a 'People' instance might be confusing or incorrect.
            # Consider if separate validation or direct checks are more appropriate here.
            # For now, keeping the original logic but noting the potential issue.

            if not validate_username(name):
                return JsonResponse({'error': 'Invalid name'}, status=400)

            # NOTE: Assuming validate_password was a typo and meant to validate something else,
            # or perhaps numberbooks validation is missing. Keeping as is for now.
            if not validate_password(numberbooks):
                return JsonResponse({'error': 'Invalid number of books'}, status=400)

            # NOTE: Assuming validate_email was a typo and meant to validate 'type'.
            # Keeping as is for now.
            if not validate_email(type):
                return JsonResponse({'error': 'Invalid type'}, status=400)
            # Simplified checks for this context:
            if People.objects.filter(name=name).exists():
                 return JsonResponse({'error': 'Person with this name already exists'}, status=400)
            if not isinstance(age, int) or age <= 0:
                 return JsonResponse({'error': 'Invalid age'}, status=400)
            if type not in [code for code, name in People.TYPES]:
                 return JsonResponse({'error': 'Invalid type'}, status=400)
            if AuthUser.objects.filter(username=name).exists():
                 return JsonResponse({'error': 'Username already taken in Auth system'}, status=400)


        
            # Create user
            People.objects.create(name=name, numberbooks=numberbooks, type=type, age=age, email=email, password=password)
            AuthUser.objects.create_user(username=name, password=password, email=email)
            return JsonResponse({'message': 'User created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)




# ============================== #
# 3️ BOOK MANAGEMENT ROUTES       #
# ============================== #

# List books view
class ListBooksView(View):
    def get(self, request):
        category_filter = request.GET.get("category") 

        books = Book.objects.all()

        if category_filter:
            books = books.filter(category=category_filter)  

        books_data = books.values(
            "id", "title", "author", "isbn", "category", "language", "condition",
            "available", "image", "due_date", "borrower_id", "storage_location",
            "publisher", "publication_year", "copy_number"
        )

        # Convert image path if needed (values() returns the string path)
        # No conversion needed here as values() gets the DB value directly.

        return JsonResponse(list(books_data), safe=False, status=200)


# Create book view
@method_decorator(csrf_exempt, name='dispatch')
class CreateBookView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title')
            author = data.get('author')
            isbn = data.get('isbn')
            category = data.get('category')
            language = data.get('language')
            condition = data.get('condition')
            available = data.get('available')
            storage_location = data.get('storageLocation') 
            publisher = data.get('publisher') 
            publication_year = data.get('publicationYear') 
            copy_number = data.get('copyNumber') 

            # --- Simplification Suggestion: Use request.user directly ---
            # The 'user' field on the Book model seems to represent the *owner* or *adder*
            # rather than the borrower. If the intent is to assign the currently logged-in
            # user as the owner, we can use request.user.
            # However, the Book model links 'user' to 'People', not 'AuthUser'.
            # This implies a need to find the 'People' instance corresponding to 'request.user'.
            # The current logic correctly fetches the People object.

            current_user_auth = request.user
            if not current_user_auth.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            # Fetch the People object associated with the authenticated user
            try:
                # Assuming 'user' field on Book means the person who added/owns it.
                book_owner_people = People.objects.get(name=current_user_auth.username)
            except People.DoesNotExist:
                # Decide how to handle this: error, or maybe allow creation without owner?
                # Current logic returns an error, which is reasonable.
                return JsonResponse({'error': 'People object not found for current user'}, status=404)
            # Validate required fields
            if not all([title, author, isbn, category, language, condition]):
                 return JsonResponse({'error': 'Missing required book fields'}, status=400)

            # Validate choices
            if category not in [code for code, name in Book.CATEGORIES]:
                 return JsonResponse({'error': 'Invalid category'}, status=400)
            if condition not in [code for code, name in Book.CONDITIONS]:
                 return JsonResponse({'error': 'Invalid condition'}, status=400)

            # Check ISBN uniqueness before creation attempt
            if Book.objects.filter(isbn=isbn).exists():
                return JsonResponse({'error': 'Book with this ISBN already exists'}, status=400)


            # Create book, assigning the current user
            due_date = datetime.now() + timedelta(weeks=2)
            Book.objects.create(
                title=title, author=author, isbn=isbn,due_date=due_date,
                category=category, language=language, user=book_owner_people, condition=condition,
                available=available, storage_location=storage_location,
                publisher=publisher, publication_year=publication_year, copy_number=copy_number
            )
            return JsonResponse({'message': 'Book created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e: # Catch other potential errors during creation
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


#Delete book view
@method_decorator(csrf_exempt, name='dispatch')
class DeleteBookView(View):
    def delete(self, request ,book_id):
        try:
            # --- Robustness Suggestion: Add permission check ---
            # Should only admins/librarians or maybe the owner be allowed to delete?
            # Add logic here to check request.user's role (via People.type)
            # Example (needs refinement based on actual roles):
            # current_user_people = People.objects.get(name=request.user.username)
            # if current_user_people.type not in ['AD', 'LB']:
            #     return JsonResponse({'error': 'Permission denied'}, status=403)
            # --- End Suggestion ---

            book = get_object_or_404(Book, id=book_id)
            book.delete()
            return JsonResponse({'message': 'Book deleted successfully'}, status=200)
        except ObjectDoesNotExist: # More specific exception
             return JsonResponse({'error': 'Book not found'}, status=404)
        except Exception as e:
            # Log the error e
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)




# Borrow book view
@method_decorator(csrf_exempt, name='dispatch')
class BorrowBookView(View): # Changed to Class-based view
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            user_id = data.get('user_id') # Get user_id (People ID) from request

            if not book_id:
                return JsonResponse({'error': 'Book ID is required'}, status=400)
            if not user_id:
                return JsonResponse({'error': 'User ID is required'}, status=400) # Ensure user_id is provided

            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                return JsonResponse({'error': 'Book not found'}, status=404)

            try:
                user = People.objects.get(id=user_id) # Get People object for borrower
            except People.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Determine if the request is from the user who currently borrowed the book
            borrowed_by_requesting_user = book.borrower == user

            message = ''
            status_code = 200

            if book.available: # Book is available, so attempt to borrow it
                # **** START: Borrow Limit Check ****
                current_borrow_count = Book.objects.filter(borrower=user, available=False).count()

                if current_borrow_count >= MAX_BORROW_LIMIT:
                    message = f'Borrow limit reached. Users can borrow a maximum of {MAX_BORROW_LIMIT} books.'
                    status_code = 400 # Bad Request - User cannot borrow more
                else:
                    # Proceed with borrowing if limit not reached
                    book.available = False
                    book.borrower = user # Assign the borrower
                    book.borrow_date = date.today() # Record borrow date using date directly
                    book.due_date = date.today() + timedelta(weeks=2) # Set due date to 2 weeks from now
                    book.save()
                    message = 'Book borrowed successfully' # Set success message
                    status_code = 200 # OK
                # **** END: Borrow Limit Check ****

            elif borrowed_by_requesting_user: # Book is borrowed by the requesting user, so return it
                book.available = True
                book.borrower = None # Clear borrower
                book.borrow_date = None # Clear borrow date
                book.due_date = None # Optionally clear or keep the last due date
                book.save()
                message = 'Book returned successfully' # Set return message
                status_code = 200 # OK
            else: # Book is borrowed by another user
                due_date_str = book.due_date.strftime("%Y-%m-%d") if book.due_date else "an unknown date"
                message = f'Book is currently unavailable. It is due back around {due_date_str}.' # Message for borrowed by others
                status_code = 400 # Bad Request - client error (cannot borrow)


            # Prepare book data for response only on success or relevant state change
            book_data = None
            if status_code == 200: # Only include book data on success
                book_data = {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'isbn': book.isbn,
                    'category': book.category,
                    'language': book.language,
                    'user_id': book.user_id, # keep owner_id for consistency if needed on frontend
                    'condition': book.condition,
                    'available': book.available,
                    'image': str(book.image), # serialize ImageField to string
                    'borrower_id': book.borrower.id if book.borrower else None, # Include borrower id
                    'borrow_date': book.borrow_date.isoformat() if book.borrow_date else None, # Include borrow date
                    'due_date': book.due_date.isoformat() if book.due_date else None # Include due_date in response
                }
                return JsonResponse({'message': message, 'book': book_data}, status=status_code)
            else:
                # For errors (like limit reached or book unavailable), just return the message
                return JsonResponse({'error': message}, status=status_code)


        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Log the error e
            print(f"Error in BorrowBookView: {e}") # Basic logging
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)


# Update Book
@method_decorator(csrf_exempt, name='dispatch')
class UpdateBookView(View):
    def put(self, request, book_id): # Changed from post to put method
        try:
            # --- Robustness Suggestion: Add permission check ---
            # Similar to DeleteBookView, check if the user has permission to update.
            # current_user_people = People.objects.get(name=request.user.username)
            # if current_user_people.type not in ['AD', 'LB']:
            #     return JsonResponse({'error': 'Permission denied'}, status=403)
            # --- End Suggestion ---

            data = json.loads(request.body)
            book = get_object_or_404(Book, id=book_id)

            # --- Robustness: Validate incoming data ---
            # Example: Check if 'category' or 'condition' are valid choices if provided
            if 'category' in data and data['category'] not in [code for code, name in Book.CATEGORIES]:
                 return JsonResponse({'error': f"Invalid category: {data['category']}"}, status=400)
            if 'condition' in data and data['condition'] not in [code for code, name in Book.CONDITIONS]:
                 return JsonResponse({'error': f"Invalid condition: {data['condition']}"}, status=400)
            if 'isbn' in data and data['isbn'] != book.isbn and Book.objects.filter(isbn=data['isbn']).exists():
                 return JsonResponse({'error': f"ISBN {data['isbn']} already exists."}, status=400)
            # ---

            # Update fields present in the request data
            for field in ['title', 'author', 'isbn', 'category', 'language', 'condition', 'available', 'storage_location', 'publisher', 'publication_year', 'copy_number']:
                if field in data:
                    setattr(book, field, data[field])

            # Handle potential ForeignKey updates if needed (e.g., changing owner 'user')
            # if 'user_id' in data:
            #    try:
            #        new_owner = People.objects.get(id=data['user_id'])
            #        book.user = new_owner
            #    except People.DoesNotExist:
            #        return JsonResponse({'error': 'New owner (user) not found'}, status=404)

            book.save()
            # Optionally return the updated book data
            # serializer = BookSerializer(book)
            # return JsonResponse({'message': 'Book updated successfully', 'book': serializer.data}, status=200)
            return JsonResponse({'message': 'Book updated successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ObjectDoesNotExist: # More specific exception
             return JsonResponse({'error': 'Book not found'}, status=404)
        except Exception as e:
            # Log the error e
            print(f"Error in UpdateBookView: {e}")
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BookDetailView(View):
    def get(self, request, book_id):
        try:
            book = get_object_or_404(Book, id=book_id)
            book_data = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "category": book.category,
                "language": book.language,
                "user_id": book.user.id if book.user else None,  # Owner of the book
                "condition": book.condition,
                "available": book.available,
                "image": str(book.image),  # Convert ImageField to string
                "borrower_id": book.borrower.id if book.borrower else None,
                "borrow_date": book.borrow_date.isoformat() if book.borrow_date else None,
                "due_date": book.due_date.isoformat() if book.due_date else None, # Handle potential None due_date
                "storage_location": book.storage_location,
                "publisher": book.publisher,
                "publication_year": book.publication_year,
                "copy_number": book.copy_number,
            }
            return JsonResponse(book_data, status=200)
        except ObjectDoesNotExist: # More specific exception
             return JsonResponse({'error': 'Book not found'}, status=404)
        except Exception as e:
            # Log the error e
            print(f"Error in BookDetailView: {e}")
            return JsonResponse({"error": "An internal server error occurred."}, status=500)


# ============================== #
# 4️ SECURITY & CSRF ROUTES       #
# ============================== #
def csrf_token_view(request):
    return JsonResponse({"csrfToken": get_token(request)})




# ============================== #
# 5️ STATIC & FRONTEND ROUTES     #
# ============================== #


# Delete user view
@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserView(View):
    def delete(self, request ,user_id): # user_id here refers to People.id
        try:
            # --- Robustness Suggestion: Add permission check ---
            # Only Admins should likely be able to delete users.
            # Check request.user's role.
            # current_user_people = People.objects.get(name=request.user.username)
            # if current_user_people.type != 'AD':
            #     return JsonResponse({'error': 'Permission denied'}, status=403)
            # Also, prevent users from deleting themselves?
            # if current_user_people.id == user_id:
            #     return JsonResponse({'error': 'Cannot delete yourself'}, status=400)
            # --- End Suggestion ---

            user_people = get_object_or_404(People, id=user_id)
            # Find the corresponding AuthUser to delete as well
            user_auth = get_object_or_404(AuthUser, username=user_people.name)

            user_auth.delete() # Delete AuthUser first (or handle dependencies)
            user_people.delete() # Then delete People instance

            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except ObjectDoesNotExist:
             return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        


class ListUsersView(generics.ListAPIView):
    # --- Suggestion: Add Permissions ---
    # Should listing all users be restricted? E.g., only Admins/Librarians?
    # from rest_framework.permissions import IsAdminUser
    # permission_classes = [IsAdminUser] # Example using DRF permissions
    # ---
    queryset = People.objects.all()
    serializer_class = PeopleSerializer


# Get User Profile
@method_decorator(csrf_exempt, name='dispatch') # Should GET requests need csrf_exempt? Usually not.
class UserProfileView(View):
    def get(self, request, user_id): # user_id refers to People.id
        try:
            # --- Suggestion: Add Permission Check? ---
            # Should any logged-in user be able to view any profile?
            # Or only their own / Admins?
            # ---
            user = get_object_or_404(People, id=user_id)
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age,
                'avatar': user.avatar,
                'type': user.type
            }
            return JsonResponse(user_data, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            print(f"Error in UserProfileView: {e}")
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)

# Update User Profile (for a specific user by ID, likely by Admin)
@method_decorator(csrf_exempt, name='dispatch')
class UpdateUserProfileView(View):
    # --- Suggestion: Use PUT or PATCH instead of POST for updates ---
    # def put(self, request, user_id):
    def post(self, request, user_id): # user_id refers to People.id
        try:
            # --- Robustness Suggestion: Add permission check ---
            # Only Admins should likely be able to update arbitrary users.
            # current_user_people = People.objects.get(name=request.user.username)
            # if current_user_people.type != 'AD':
            #     return JsonResponse({'error': 'Permission denied'}, status=403)
            # --- End Suggestion ---

            data = json.loads(request.body)
            user = get_object_or_404(People, id=user_id)
            original_username = user.name # Store original username if it might change

            # --- Robustness: Validate incoming data ---
            if 'email' in data and People.objects.filter(email=data['email']).exclude(id=user_id).exists():
                 return JsonResponse({'error': 'Email already in use by another user'}, status=400)
            if 'name' in data and data['name'] != original_username:
                 if People.objects.filter(name=data['name']).exists():
                      return JsonResponse({'error': 'Name already in use by another user'}, status=400)
                 if AuthUser.objects.filter(username=data['name']).exists():
                      return JsonResponse({'error': 'Name already exists in authentication system'}, status=400)
            if 'type' in data and data['type'] not in [code for code, name in People.TYPES]:
                 return JsonResponse({'error': 'Invalid user type'}, status=400)
            # ---

            # Update fields from data
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.age = data.get('age', user.age)
            user.type = data.get('type', user.type) # Allow updating type
            # user.avatar = data.get('avatar', user.avatar) # People model doesn't have 'avatar'

            # --- Sync with AuthUser if name/email changed ---
            auth_user = None
            try:
                auth_user = AuthUser.objects.get(username=original_username)
                auth_user_updated = False
                if user.name != original_username:
                    auth_user.username = user.name
                    auth_user_updated = True
                if 'email' in data and data['email'] != auth_user.email:
                    auth_user.email = data['email']
                    auth_user_updated = True
                # Password update should likely be a separate endpoint/process
                if auth_user_updated:
                    auth_user.save()
            except AuthUser.DoesNotExist:
                print(f"Warning: AuthUser not found for People user {original_username} during update.")
            # ---

            user.save() # Save People instance changes
            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error in UpdateUserProfileView: {e}")
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)




# Update Profile (for the currently logged-in user)
@csrf_exempt # Keep for POST
def update_profile(request):
    if request.method == "POST":
        # --- Suggestion: Use PUT or PATCH for updates ---
        # if request.method in ["PUT", "PATCH"]:
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            data = json.loads(request.body)
            user = request.user # This is the AuthUser instance

            # Find the corresponding People instance
            try:
                people_instance = People.objects.get(name=user.username)
            except People.DoesNotExist:
                return JsonResponse({"error": "Associated profile data not found."}, status=404)


            # --- Validate incoming data ---
            new_username = data.get("username", user.username)
            new_email = data.get("email", user.email)

            if new_username != user.username:
                 if AuthUser.objects.filter(username=new_username).exists():
                      return JsonResponse({"error": "Username already taken"}, status=400)
                 if People.objects.filter(name=new_username).exists():
                      return JsonResponse({"error": "Username already taken in People records"}, status=400)

            if new_email != user.email:
                 if AuthUser.objects.filter(email=new_email).exists():
                      return JsonResponse({"error": "Email already in use"}, status=400)
                 if People.objects.filter(email=new_email).exists():
                      return JsonResponse({"error": "Email already in use in People records"}, status=400)
            # ---

            # Update AuthUser fields
            auth_user_updated = False
            if "username" in data and data["username"] != user.username:
                user.username = data["username"]
                auth_user_updated = True

            if "email" in data and data["email"] != user.email:
                user.email = data["email"]
                auth_user_updated = True

            if "password" in data and data["password"]: # Check if password is provided and not empty
                # Add password validation here if desired (e.g., complexity)
                user.set_password(data["password"])  # Hash password
                auth_user_updated = True
            if auth_user_updated:
                user.save()


            if "avatar" in data:
                # Assuming 'avatar' is a field on the AuthUser model or a related profile model
                # If 'avatar' is only on the 'People' model, this needs adjustment
                # For now, assuming it might be on AuthUser or a related profile accessible via user
                # This part might need refinement based on your actual User model structure
                try:
                    # Example: If you have a OneToOneField profile
                    # user.profile.avatar = data["avatar"]
                    # user.profile.save()
                    # Or if avatar is directly on a custom user model:
                    # user.avatar = data["avatar"] # This line might cause an error if 'avatar' isn't on AuthUser
                    # For now, let's assume we update the People model separately if needed
                    pass # Placeholder - update People model below if necessary
                except AttributeError:
                     # Handle case where avatar is not directly on user model
                     pass


            user.save() # Save AuthUser changes (username, email, password hash)

            # Update corresponding People instance if necessary
            try:
                people_instance = People.objects.get(name=old_username) # Find based on old username before potential change
                people_updated = False
                if "username" in data and data["username"] != people_instance.name:
                    people_instance.name = data["username"] # Keep People.name in sync
                    people_updated = True
                if "email" in data and data["email"] != people_instance.email:
                    people_instance.email = data["email"] # Keep People.email in sync
                    people_updated = True
                if "age" in data and data["age"] != people_instance.age:
                    people_instance.age = data["age"]
                    people_updated = True
                # Add other People fields if they are updatable via this endpoint (e.g., 'avatar' if added)
                # if "avatar" in data and hasattr(people_instance, 'avatar') and data["avatar"] != people_instance.avatar:
                #      people_instance.avatar = data["avatar"]
                #      people_updated = True

                if people_updated:
                    people_instance.save()

            except People.DoesNotExist:
                # Handle case where People instance doesn't exist (maybe log it)
                pass


            # Update session hash if password or username changed to prevent logout
            if "password" in data and data["password"] or ("username" in data and data["username"] != request.user.username):
                 update_session_auth_hash(request, user)

            # ✅ Ensure session is modified so Django doesn't invalidate it
            request.session.modified = True

            # Fetch the potentially updated avatar for the response
            final_avatar = "default.svg" # Default
            try:
                # Try fetching the updated People instance again
                updated_people = People.objects.get(name=user.username)
                if hasattr(updated_people, 'avatar'):
                    final_avatar = updated_people.avatar
            except People.DoesNotExist:
                pass # Keep default avatar


            return JsonResponse({
                "message": "Profile updated successfully",
                "username": user.username, # Send back the current username
                "email": user.email,
                "avatar": final_avatar,
                # "old_username": old_username # Maybe remove for production
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            # Log the exception e for debugging
            print(f"Error during profile update: {e}") # Basic logging
            return JsonResponse({"error": "An internal error occurred during profile update."}, status=500) # Generic error

    return JsonResponse({"error": "Invalid request method"}, status=405)


# NOTE: NEEDS REFACTORING! Duplicate get_current_user definition. The CurrentUserView class handles this.

def get_current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        # Use request.user.username which comes from the authenticated session
        people = People.objects.get(name=request.user.username)
        return JsonResponse({
            "id": people.id,
            "username": people.name, # Or request.user.username, should be the same
            "email": people.email, # Or request.user.email if synced
            "avatar": people.avatar if hasattr(people, 'avatar') else "default.svg",
            "role": people.type, # Renamed 'type' to 'role' for clarity, adjust if needed
        })
    except People.DoesNotExist:
         # If the People object doesn't exist, maybe return basic AuthUser info?
         # Or return an error as it implies data inconsistency.
         # Current behavior: return 404
        return JsonResponse({"error": "Associated user profile data not found."}, status=404)
    except Exception as e:
        # Log the exception e
        print(f"Error in get_current_user: {e}")
        return JsonResponse({"error": "An internal error occurred."}, status=500)