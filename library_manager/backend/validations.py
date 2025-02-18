import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_username(username):
    if not username:
        raise ValidationError("Username is required")
    if User.objects.filter(username=username).exists():
        raise ValidationError("Username already exists")
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")

def validate_password(password):
    if not password:
        raise ValidationError("Password is required")
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long")
    if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one uppercase letter and one number")

def validate_email(email):
    if not email:
        raise ValidationError("Email is required")
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already in use")

def calculate_age(birth_date):
    today = datetime.today()
    birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
    age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
    return age

def validate_birth_date(birth_date):
    if not birth_date:
        raise ValidationError("Birth date is required")
    try:
        age = calculate_age(birth_date)
        if age < 16:
            raise ValidationError("You must be at least 16 years old to register")
    except ValueError:
        raise ValidationError("Invalid birth date format. Use YYYY-MM-DD")
