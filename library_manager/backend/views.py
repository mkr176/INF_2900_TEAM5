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


@method_decorator(login_required, name='dispatch')
class MyBorrowedBooksView(View):
    def get(self, request):
        user = request.user
        try:
            people_user = People.objects.get(id=user.id)

            # Filtrar los libros que están prestados al usuario actual
            borrowed_books = Book.objects.filter(borrower=people_user, available=False)

            # Serializar los datos de los libros
            borrowed_books_data = [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "category": book.category,
                    "language": book.language,
                    "condition": book.condition,
                    "image": str(book.image),
                    "due_date": book.due_date.isoformat(),
                }
                for book in borrowed_books
            ]

            return JsonResponse({"borrowed_books": borrowed_books_data}, status=200)
        except People.DoesNotExist:
            return JsonResponse({"error": "User profile not found"}, status=404)


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

            # Get current user from request
            current_user_auth = request.user
            if not current_user_auth.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            # Fetch the People object associated with the authenticated user
            try:
                current_user_people = People.objects.get(name=current_user_auth.username)
            except People.DoesNotExist:
                return JsonResponse({'error': 'People object not found for current user'}, status=404)


            # Create book, assigning the current user
            due_date = datetime.now() + timedelta(weeks=2)
            Book.objects.create(
                title=title, author=author, isbn=isbn,due_date=due_date,
                category=category, language=language, user=current_user_people, condition=condition, # Assign current_user_people
                available=available, storage_location=storage_location,
                publisher=publisher, publication_year=publication_year, copy_number=copy_number
            )
            return JsonResponse({'message': 'Book created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        
#Delete book view
@method_decorator(csrf_exempt, name='dispatch')
class DeleteBookView(View):
    def delete(self, request ,book_id):
        try:
            book = get_object_or_404(Book, id=book_id)
            book.delete()
            return JsonResponse({'message': 'Book deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        



# Borrow book view
@method_decorator(csrf_exempt, name='dispatch')
class BorrowBookView(View): # Changed to Class-based view
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            user_id = data.get('user_id') # Get user_id from request
            new_condition = data.get('condition') # Get new condition from request

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

            borrowed_by_current_user = book.borrower == user

            if book.available: # Book is available, so borrow it
                book.available = False
                book.borrower = user # Assign the borrower
                book.borrow_date = datetime.now().date() # Record borrow date
                book.due_date = datetime.now().date() + timedelta(weeks=2) # Set due date to 2 weeks from now
                book.save()
                message = 'Book borrowed successfully' # Set success message
                status_code = 200 # OK
            elif borrowed_by_current_user: # Book is borrowed by the current user, so return it
                book.available = True
                book.borrower = None # Clear borrower
                book.borrow_date = None # Clear borrow date
                book.condition = new_condition # Update condition if provided
                # book.due_date = datetime.now().date() + timedelta(weeks=2) #reset due date for next borrow
                book.save()
                message = 'Book returned successfully' # Set return message
                status_code = 200 # OK
            else: # Book is borrowed by another user
                availability_date = book.due_date.strftime("%Y-%m-%d")
                message = f'Book is currently unavailable. It will be available from {availability_date}' # Message for borrowed by others
                status_code = 400 # Bad Request - client error


            book_data = { # Prepare book data for response
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'category': book.category,
                'language': book.language,
                'user_id': book.user_id, # keep user_id for consistency if needed on frontend
                'condition': book.condition,
                'available': book.available,
                'image': str(book.image), # serialize ImageField to string
                'borrower_id': book.borrower.id if book.borrower else None, # Include borrower id
                'borrow_date': book.borrow_date.isoformat() if book.borrow_date else None, # Include borrow date
                'due_date': book.due_date.isoformat() # Include due_date in response
            }
            return JsonResponse({'message': message, 'book': book_data}, status=status_code) # Return success with appropriate message and book data


        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Update Book
@method_decorator(csrf_exempt, name='dispatch')
class UpdateBookView(View):
    def put(self, request, book_id): # Changed from post to put method
        try:
            data = json.loads(request.body)
            book = get_object_or_404(Book, id=book_id)

            for field in ['title', 'author', 'isbn', 'category', 'language', 'condition', 'available', 'storage_location', 'publisher', 'publication_year', 'copy_number']:
                if field in data:
                    setattr(book, field, data[field])

            book.save()
            return JsonResponse({'message': 'Book updated successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


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
                "user_id": book.user.id,  # Owner of the book
                "condition": book.condition,
                "available": book.available,
                "image": str(book.image),  # Convert ImageField to string
                "borrower_id": book.borrower.id if book.borrower else None,
                "borrow_date": book.borrow_date.isoformat() if book.borrow_date else None,
                "due_date": book.due_date.isoformat(),
                "storage_location": book.storage_location,
                "publisher": book.publisher,
                "publication_year": book.publication_year,
                "copy_number": book.copy_number,
            }
            return JsonResponse(book_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


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
    def delete(self, request ,user_id):
        try:
            user = get_object_or_404(People, id=user_id)
            user2 = get_object_or_404(AuthUser, username=user.name)
            user2.delete()
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
@method_decorator(login_required, name='dispatch')
class CurrentUserView(View):
    def get(self, request):
        user = request.user
        try:
            people = People.objects.get(name=user.username)
            user_data = {
                'id': people.id, 
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


class ListUsersView(generics.ListAPIView):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer


# Get User Profile
@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(View):
    def get(self, request, user_id):
        try:
            user = People.objects.get(id=user_id)
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'age': user.age,
                'avatar': user.avatar,
                'type': user.type
            }
            return JsonResponse(user_data, status=200)
        except People.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

# Update User Profile
@method_decorator(csrf_exempt, name='dispatch')
class UpdateUserProfileView(View):
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            user = People.objects.get(id=user_id)

            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.age = data.get('age', user.age)
            user.avatar = data.get('avatar', user.avatar)  # Update avatar

            user.save()
            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        except People.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)





@login_required
def get_user_info(request):
    if request.user.is_authenticated:
        try:
            person = People.objects.get(name=request.user.username)
            return JsonResponse({
                "username": person.name,
                "email": person.email,
                "avatar": person.avatar if hasattr(person, 'avatar') else "default.svg",
                "type": person.type,
            })
        except People.DoesNotExist:
           
            return JsonResponse({"error": "Unauthorized"}, status=401)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)

@csrf_exempt
def update_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Store old username for debugging
            old_username = user.username  

            # Update fields
            if "username" in data and data["username"] != user.username:
                user.username = data["username"]

            if "email" in data:
                user.email = data["email"]

            if "password" in data and data["password"] != "":
                user.set_password(data["password"])  # Django's hashing

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
                if "username" in data and data["username"] != old_username:
                    people_instance.name = data["username"] # Update name in People too
                    people_updated = True
                if "email" in data and data["email"] != people_instance.email:
                     people_instance.email = data["email"]
                     people_updated = True
                if "avatar" in data and hasattr(people_instance, 'avatar') and data["avatar"] != people_instance.avatar:
                     people_instance.avatar = data["avatar"]
                     people_updated = True

                if people_updated:
                    people_instance.save()

            except People.DoesNotExist:
                # Handle case where People instance doesn't exist (maybe log it)
                pass


            # ✅ Prevent logout by updating session authentication hash
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