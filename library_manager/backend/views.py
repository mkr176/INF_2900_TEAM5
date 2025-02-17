from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json

# Create your views here.
def front (request, *args, **kwargs):
    # return render(request, 'new.html')
    return render(request, 'startpage.html') # Changed template name here

from django.contrib.auth.models import User
from django.http import JsonResponse

# Register View
class RegisterView(View):
    def post(self, request):
        try:
            # Parse JSON body
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')

            # Validation checks
            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)
            if len(password) < 6:
                return JsonResponse({'error': 'Password must be at least 6 characters long'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create the user
            User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

# Login View
class LoginView(View):
    def post(self, request):
        try:
            # Parse JSON body
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Validate input
            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            # Authenticate the user
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
        # Log the user out
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=200)