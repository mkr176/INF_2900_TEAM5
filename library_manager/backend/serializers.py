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
    # Explicitly add avatar_url field for reading
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        # Fields from UserProfile model + username/id from related User
        fields = [
            "user_id",
            "username",
            "type",
            "age",
            "avatar", # Keep the original field for write operations if needed elsewhere
            "avatar_url", # Add the URL field for reading
            "get_type_display",
        ]  # get_type_display provides human-readable type
        read_only_fields = [
            "username",
            "user_id",
            "get_type_display",
            "avatar_url", # URL is read-only
        ]
        # Make the 'avatar' field write-only in this context if it's only meant
        # to be *read* via avatar_url and *written* via the custom view logic.
        # However, keeping it allows potential future file uploads via other views.
        # Let's keep it for now, the view logic handles the string update.
        # extra_kwargs = {
        #     'avatar': {'write_only': True}
        # }

    def get_avatar_url(self, obj):
        """
        Return the full URL for the avatar.
        Handles cases where avatar might be None or have no file.
        """
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            # Use request to build absolute URI if available
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            # Fallback to just the URL path if no request context
            return obj.avatar.url
        # Provide a default URL if no avatar is set or file is missing
        # This should ideally point to your actual default static file URL
        # Assuming default is 'avatars/default.svg' and served under STATIC_URL
        from django.templatetags.static import static
        default_url = static('images/avatars/default.svg') # Adjust path if needed
        if request:
            return request.build_absolute_uri(default_url)
        return default_url


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

    def validate_username(self, value):
        """Check that the username is not already taken."""
        if User.objects.filter(username__iexact=value).exists(): # Case-insensitive check
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        """Check that the email is not already taken."""
        if User.objects.filter(email__iexact=value).exists(): # Case-insensitive check
            raise serializers.ValidationError("A user with that email address already exists.")
        return value

    def validate(self, attrs):
        # Check if passwords match (keep this check)
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        # Remove confirmation password field after validation
        attrs.pop("password2")
        # Username and Email uniqueness are now handled by validate_username/validate_email
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
    # <<< FIX: Add image_url for books >>>
    image_url = serializers.SerializerMethodField()

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
            "image", # Keep original field for potential uploads/reference
            "image_url", # Add URL field for reading
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
            "borrower", "borrower_id", "borrow_date", "due_date",
            "added_by", "added_by_id", "category_display", "condition_display",
            "available", "days_left", "overdue", "days_overdue", "due_today",
            "image_url", # URL is read-only
        ]
        # Optionally make 'image' write-only if only URL is needed for read
        # extra_kwargs = {
        #     'image': {'write_only': True}
        # }

    # <<< FIX: Add method to get book image URL >>>
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        # Provide default book image URL
        from django.templatetags.static import static
        # Ensure this path matches your actual default image location within static files
        default_url = static('images/library_seal.jpg')
        if request:
            return request.build_absolute_uri(default_url)
        return default_url

    def get_days_left(self, obj):
        # Ensure due_date is compared with today's date
        if obj.due_date and not obj.available:
            today = date.today()
            # Check if due_date is actually a date object
            if isinstance(obj.due_date, date):
                return (obj.due_date - today).days
            else:
                # Attempt to parse if it's a string (though it should be a date from the model)
                try:
                    due_date_obj = date.fromisoformat(str(obj.due_date))
                    return (due_date_obj - today).days
                except (ValueError, TypeError):
                    return None # Cannot calculate if format is wrong
        return None

    def get_overdue(self, obj):
        days_left = self.get_days_left(obj)
        return days_left is not None and days_left < 0

    def get_days_overdue(self, obj):
        days_left = self.get_days_left(obj) # Use the calculated days_left
        if days_left is not None and days_left < 0:
            return abs(days_left)
        return 0 # Return 0 if not overdue or days_left is None

    def get_due_today(self, obj):
        days_left = self.get_days_left(obj)
        return days_left is not None and days_left == 0
