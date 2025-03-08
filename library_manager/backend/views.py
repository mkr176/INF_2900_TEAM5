from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User as AuthUser # Alias Django's User model to avoid confusion
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from .serializers import UserSerializer, CustomUserSerializer, BookSerializer 
from .validations import validate_username, validate_password, validate_email, validate_birth_date
from .models import User as CustomUser # Import your custom User model
from .models import Book


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

            # Check if user already exists - use Django's AuthUser here
            if AuthUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create user - use Django's AuthUser here
            AuthUser.objects.create_user(username=username, password=password, email=email)
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


class ListUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all() # Use your custom User model here
    serializer_class = CustomUserSerializer # Use CustomUserSerializer


class ListBooksView(generics.ListAPIView): # Create ListBooksView
    queryset = Book.objects.all()
    serializer_class = BookSerializer