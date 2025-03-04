from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from .validations import validate_username, validate_password, validate_email, validate_birth_date
from .models import Book
from django.shortcuts import get_object_or_404
from datetime import datetime
from datetime import timedelta
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
            birth_date = data.get('birthDate', '')

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create user
            User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

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
class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=200)
    
# List books view
def list_books(request):
    books = Book.objects.all().values('id', 'title', 'author', 'isbn', 'category', 'language', 'user_id', 'condition', 'available', 'image')
    return JsonResponse(list(books), safe=False)
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
            user_id = data.get('userId')
            condition = data.get('condition')
            available = data.get('available')

            # Check if user exists
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({'error': 'User does not exist'}, status=400)

            # Create book
            due_date = datetime.now + timedelta(weeks=2)
            user = User.objects.get(id=user_id)
            Book.objects.create(
                title=title, author=author, isbn=isbn,due_date=due_date,
                category=category, language=language, user=user, condition=condition,
                available=available
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
            User.objects.create(name=name, numberbooks=numberbooks, type=type, age=age, email=email, password=password)
            return JsonResponse({'message': 'User created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
# Delete user view
@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserView(View):
    def delete(self, request ,user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ListUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer