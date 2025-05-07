from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Book, UserProfile
from datetime import date  # Import date
from django.templatetags.static import static # Import static tag function
from django.conf import settings  # Import settings for STATIC_URL

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
        Return the full URL for the avatar, ensuring it points to the static path.
        Handles cases where avatar might be None or have no file/name.
        """
        request = self.context.get('request')
        avatar_path = None

        # Check if obj.avatar has a meaningful value (name attribute)
        # This handles both ImageField/FileField and potentially CharField if used
        if obj.avatar and hasattr(obj.avatar, 'name') and obj.avatar.name:
            # Assume obj.avatar.name stores the path relative to MEDIA_ROOT or
            # just the filename if it's a static choice.
            # We need to construct the path relative to the STATIC_URL base.
            # Example: If avatar.name is 'avatars/user-1.svg', we want
            # '/static/images/avatars/user-1.svg'
            # If avatar.name is just 'user-1.svg', we need to prepend 'images/avatars/'
            # Let's assume the name includes the 'avatars/' prefix as saved by the view.
            # If not, adjust the path construction here.
            if 'avatars/' in obj.avatar.name:
                 # Construct the path expected by the static tag function
                 # e.g., 'images/avatars/user-1.svg'
                 static_file_path = f"images/{obj.avatar.name}"
                 avatar_path = static(static_file_path)
            else:
                 # Fallback or alternative logic if 'avatars/' prefix is missing
                 # Maybe the name is just the filename?
                 static_file_path = f"images/avatars/{obj.avatar.name}"
                 avatar_path = static(static_file_path)

        # If no valid avatar path was derived, use the default
        if not avatar_path:
            avatar_path = static('images/avatars/default.svg') # Default path

        # Build the absolute URI if request context is available
        if request:
            return request.build_absolute_uri(avatar_path)
        # Otherwise, return the path (e.g., /static/images/avatars/...)
        return avatar_path


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
    # borrower = serializers.StringRelatedField(read_only=True) # Old field
    borrower = serializers.SerializerMethodField() # New: Use a method field

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
            # "borrower", # Removed: SerializerMethodField is read-only by default
            "borrower_id", "borrow_date", "due_date",
            "added_by", "added_by_id", "category_display", "condition_display",
            "available", "days_left", "overdue", "days_overdue", "due_today",
            "image_url", # URL is read-only
        ]
        # Optionally make 'image' write-only if only URL is needed for read
        # extra_kwargs = {
        #     'image': {'write_only': True}
        # }
    def get_borrower(self, obj: Book) -> str | None:
        """
        Determines what to display for the 'borrower' field based on the
        requesting user's role and whether they are the borrower.
        """
        request = self.context.get('request')
        
        # If the book is not borrowed, borrower is None
        if not obj.borrower:
            return None

        # If there's a request and an authenticated user
        if request and request.user and request.user.is_authenticated:
            # Case 1: The current user is the borrower
            if request.user == obj.borrower:
                return obj.borrower.username
            
            # Case 2: The current user is an Admin or Librarian
            # (and not the borrower, due to previous check)
            user_profile = getattr(request.user, 'profile', None)
            if user_profile and user_profile.type in ['AD', 'LB']:
                return obj.borrower.username
        
        # Case 3: For regular users viewing a book borrowed by someone else,
        # or for unauthenticated users (if a view ever allows it for borrowed books).
        return "Checked Out" # Generic placeholder for privacy


    def get_image_url(self, obj):
        """
        Return the full URL for the book cover image.
        Handles potential incorrect prefixes in the stored image name
        and ensures the path is correctly resolved using the static tag.
        """
        request = self.context.get('request')
        image_path_resolved = None # The final path/URL
        default_static_path = 'images/library_seal.jpg' # Default image relative to static root

        # Similar logic for book images if they are static assets
        if obj.image and hasattr(obj.image, 'name') and obj.image.name:
            image_name = obj.image.name.strip() # Get the stored name and strip whitespace

            # --- Clean the stored image name ---
            # Remove potential leading prefixes that might have been saved incorrectly
            prefixes_to_remove = ['static/images/', '/static/images/', 'images/']
            for prefix in prefixes_to_remove:
                if image_name.startswith(prefix):
                    image_name = image_name[len(prefix):]
                    break # Remove only the first matching prefix

            # --- Construct the path for the static tag ---
            # We assume all book images belong under an 'images/' directory
            # within the static files structure.
            # If image_name is 'covers/book.jpg', static_file_path becomes 'images/covers/book.jpg'
            # If image_name is 'book.jpg', static_file_path becomes 'images/book.jpg'
            static_file_path = f"images/{image_name}"

            try:
                # static() will prepend STATIC_URL ('/static/')
                # e.g., static('images/covers/book.jpg') -> '/static/images/covers/book.jpg'
                image_path_resolved = static(static_file_path)
            except (ValueError, FileNotFoundError): # Handle case where static file doesn't exist
                print(f"Warning: Static file not found for book image: '{static_file_path}' (derived from '{obj.image.name}'). Using default.")
                image_path_resolved = None # Fallback to default

        # If no valid image path or static file not found, use the default
        if not image_path_resolved:
            try:
                image_path_resolved = static(default_static_path)
            except (ValueError, FileNotFoundError):
                 print(f"Warning: Default static file not found: '{default_static_path}'")
                 # If even the default is missing, return a placeholder or None
                 # Returning the path string directly might be better than None if build_absolute_uri fails
                 image_path_resolved = f"{settings.STATIC_URL}{default_static_path}" # Construct manually as last resort


        # Build the absolute URI if request context is available
        if request and image_path_resolved:
            try:
                return request.build_absolute_uri(image_path_resolved)
            except Exception as e:
                 print(f"Error building absolute URI for '{image_path_resolved}': {e}")
                 # Fallback if build_absolute_uri fails unexpectedly
                 return image_path_resolved # Return the path itself (/static/...)
        elif image_path_resolved:
             return image_path_resolved # Return the path (/static/...) if no request
        else:
             return None # Should ideally not happen if default exists

    def get_days_left(self, obj):
        # Ensure due_date is compared with today's date
        if obj.due_date and not obj.available:
            today = date.today()
            # Check if due_date is actually a date object
            if isinstance(obj.due_date, date):
                delta = obj.due_date - today
                return delta.days
            else:
                # Attempt to parse if it's a string (though it should be a date from the model)
                try:
                    due_date_obj = date.fromisoformat(str(obj.due_date))
                    delta = due_date_obj - today
                    return delta.days
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
