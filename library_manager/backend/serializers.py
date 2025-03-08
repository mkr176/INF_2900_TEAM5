from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User as CustomUser # Import your custom User model
from .models import Book

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class CustomUserSerializer(serializers.ModelSerializer): # Serializer for your custom User model
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'numberbooks', 'type'] # Include the fields you want to serialize

class BookSerializer(serializers.ModelSerializer): # Serializer for Book model
    class Meta:
        model = Book
        fields = '__all__' # Or specify the fields you want to serialize, e.g., ['id', 'title', 'author', ...]