from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
import json
from .validations import validate_username, validate_password, validate_email, validate_birth_date

# Landing Page View
def front(request, *args, **kwargs):
    return render(request, 'startpage.html')  # Changed template name


class FrontendAppView(TemplateView):
    template_name = "frontend/index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# Register View
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            birth_date = data.get('birthDate', '')

            # Run validations
            try:
                validate_username(username)
                validate_password(password)
                validate_email(email)
                validate_birth_date(birth_date)
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=400)

            # Create the user
            user = User.objects.create_user(username=username, password=password, email=email)
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
