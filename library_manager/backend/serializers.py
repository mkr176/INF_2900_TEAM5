from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Book,People

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class CustomUserSerializer(serializers.ModelSerializer): # Serializer for your custom User model
    class Meta:
        model = People
        fields = ['id', 'name', 'numberbooks', 'type','age','email','password'] # Include the fields you want to serialize

class BookSerializer(serializers.ModelSerializer): # Serializer for Book model
    class Meta:
        model = Book
        fields = '__all__' # Or specify the fields you want to serialize, e.g., ['id', 'title', 'author', ...]