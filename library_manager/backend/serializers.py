from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Book, UserProfile
from datetime import date  # Import date

# Get the User model configured in settings (usually django.contrib.auth.models.User)
User = get_user_model()


# Serializer for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    # Make the 'user' field read-only if included, but typically it's accessed via the UserSerializer
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    # Or display username for context
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserProfile
        # Fields from UserProfile model + username/id from related User
        fields = [
            "user_id",
            "username",
            "type",
            "age",
            "avatar",
            "get_type_display",
        ]  # get_type_display provides human-readable type
        read_only_fields = [
            "username",
            "user_id",
            "get_type_display",
        ]  # These are derived or read-only


# Serializer for the standard User model, including nested profile data
class UserSerializer(serializers.ModelSerializer):
    # Nest the UserProfileSerializer. 'profile' is the related_name we set in models.py
    # read_only=True because profile creation/update might be handled separately or during user creation
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        # Include fields from User model AND the nested profile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
            "date_joined",
            "is_staff",
        ]
        # Ensure password is never sent
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },  # Password is write-only, not required for updates unless changing it
            "date_joined": {"read_only": True},  # Usually read-only
            "is_staff": {
                "read_only": True
            },  # Usually read-only unless managed by admin endpoint
        }


# Serializer specifically for User Registration
class RegisterSerializer(serializers.ModelSerializer):
    # Explicitly declare password fields for validation
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm password"
    )
    # Include profile fields that can be set during registration
    type = serializers.ChoiceField(
        choices=UserProfile.TYPES, required=False
    )  # Optional, defaults to 'US' in model
    age = serializers.IntegerField(required=False, allow_null=True)
    email = serializers.EmailField(
        required=True
    )  # Make email required for registration
    # Add min_length validation for username
    username = serializers.CharField(required=True, min_length=3)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "type",
            "age",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        # Remove confirmation password field after validation
        attrs.pop("password2")
        # Username and Email uniqueness are handled by the model's unique=True constraints implicitly
        return attrs

    def create(self, validated_data):
        # Separate profile data from user data
        profile_data = {
            "type": validated_data.pop("type", "US"),  # Default to 'US' if not provided
            "age": validated_data.pop("age", None),
        }
        # Use create_user to handle password hashing
        user = User.objects.create_user(**validated_data)
        # Create the associated UserProfile
        UserProfile.objects.create(user=user, **profile_data)
        return user


# Serializer for the Book model
class BookSerializer(serializers.ModelSerializer):
    # Use StringRelatedField to display usernames instead of IDs for related users
    # read_only=True because these fields are typically set by the view logic (e.g., current user)
    # or determined by borrowing actions, not directly submitted in book creation/update data.
    added_by = serializers.StringRelatedField(read_only=True)
    borrower = serializers.StringRelatedField(read_only=True)

    # Add read-only fields for convenience in API responses
    borrower_id = serializers.PrimaryKeyRelatedField(source="borrower", read_only=True)
    added_by_id = serializers.PrimaryKeyRelatedField(source="added_by", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )

    # Derived fields for borrowed books
    days_left = serializers.SerializerMethodField()
    overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    due_today = serializers.SerializerMethodField()

    class Meta:
        model = Book
        # Explicitly list all fields you want to expose
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "category",
            "category_display",
            "language",
            "condition",
            "condition_display",
            "available",
            "image",
            "borrower",
            "borrower_id",
            "borrow_date",
            "due_date",
            "storage_location",
            "publisher",
            "publication_year",
            "copy_number",
            "added_by",
            "added_by_id",
            # Add derived fields to the list
            "days_left",
            "overdue",
            "days_overdue",
            "due_today",
        ]
        read_only_fields = [
            "borrower",
            "borrower_id",
            "borrow_date",
            "due_date",  # Managed by borrow/return logic
            "added_by",
            "added_by_id",  # Set automatically based on logged-in user
            "category_display",
            "condition_display",  # Read-only representations
            "available",  # Ensure availability is only changed via borrow/return endpoints
            # Derived fields are inherently read-only
            "days_left",
            "overdue",
            "days_overdue",
            "due_today",
        ]
        # Example: Make 'available' read-only if it's only changed via borrow/return actions
        # extra_kwargs = {
        #     'available': {'read_only': True} # This is now handled by adding 'available' to read_only_fields
        # }

    def get_days_left(self, obj):
        if obj.due_date and not obj.available:
            return (obj.due_date - date.today()).days
        return None  # Or 0, or some other indicator if not borrowed/due

    def get_overdue(self, obj):
        days_left = self.get_days_left(obj)
        return days_left is not None and days_left < 0

    def get_days_overdue(self, obj):
        if self.get_overdue(obj):
            return abs(self.get_days_left(obj))
        return 0

    def get_due_today(self, obj):
        days_left = self.get_days_left(obj)
        return days_left is not None and days_left == 0
