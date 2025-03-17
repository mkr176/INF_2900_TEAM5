from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User as AuthUser # Alias Django's User model to avoid confusion
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from .serializers import UserSerializer, PeopleSerializer
from .validations import validate_username, validate_password, validate_email, validate_birth_date

from .models import Book,People
from django.shortcuts import get_object_or_404
from datetime import datetime
from datetime import timedelta

from django.contrib.auth.models import User
from django.middleware.csrf import get_token

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash


User = get_user_model()



# Landing Page View
def front(request, *args, **kwargs):
    return render(request, 'startpage.html')  # Changed template name


class FrontendAppView(TemplateView):
    template_name = "frontend/index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

# Logout View
@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request):
        logout(request)  # Clears session
        return JsonResponse({"message": "Logged out successfully"}, status=200)

# List books view
def list_books(request):
    books = Book.objects.all().values('id', 'title', 'author', 'isbn', 'category', 'language', 'user_id', 'condition', 'available', 'image', 'due_date', 'borrower_id', 'borrow_date', 'storage_location', 'publisher', 'publication_year', 'copy_number') # added due_date, borrower_id, borrow_date, storage_location, publisher, publication_year, copy_number
    return JsonResponse(list(books), safe=False)

# Borrow book view
@method_decorator(csrf_exempt, name='dispatch')

class BorrowBookView(View): # Changed to Class-based view
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            user_id = data.get('user_id') # Get user_id from request

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
                book.save()
                message = 'Book borrowed successfully' # Set success message
                status_code = 200 # OK
            elif borrowed_by_current_user: # Book is borrowed by the current user, so return it
                book.available = True
                book.borrower = None # Clear borrower
                book.borrow_date = None # Clear borrow date
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

            if not validate_password(numberbooks):
                return JsonResponse({'error': 'Invalid number of books'}, status=400)

            if not validate_email(type):
                return JsonResponse({'error': 'Invalid type'}, status=400)

        
            # Create user
            People.objects.create(name=name, numberbooks=numberbooks, type=type, age=age, email=email, password=password)
            User.objects.create_user(username=name, password=password, email=email)
            return JsonResponse({'message': 'User created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
# Delete user view
@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserView(View):
    def delete(self, request ,user_id):
        try:
            user = get_object_or_404(People, id=user_id)
            user2= get_object_or_404(User, id=user_id)
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



def csrf_token_view(request):
    return JsonResponse({"csrfToken": get_token(request)})


@login_required
def get_user_info(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "username": request.user.username,
            "email": request.user.email,
        })
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
                user.avatar = data["avatar"]

            user.save()

            # ✅ Prevent logout by updating session authentication hash
            update_session_auth_hash(request, user)  

            # ✅ Ensure session is modified so Django doesn't invalidate it
            request.session.modified = True

            return JsonResponse({
                "message": "Profile updated successfully",
                "new_username": user.username,
                "old_username": old_username
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def get_current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        people = People.objects.get(name=request.user.username)
        return JsonResponse({
            "id": people.id,
            "username": people.name,
            "email": people.email,
            "avatar": people.avatar,
            "role": people.type,
        })
    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not found in database"}, status=404)