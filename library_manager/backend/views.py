import json
from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.middleware.csrf import get_token
from django.db.models import Count

from rest_framework import generics, status, permissions, filters, views as drf_views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes

# Use django-filter for advanced filtering if installed, otherwise use DRF defaults
try:
    from django_filters.rest_framework import DjangoFilterBackend
    DEFAULT_FILTER_BACKENDS = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
except ImportError:
    DEFAULT_FILTER_BACKENDS = [filters.SearchFilter, filters.OrderingFilter]


from .models import Book, UserProfile
from .serializers import (
    UserSerializer, RegisterSerializer, BookSerializer, UserProfileSerializer
)

# Define the borrow limit constant
MAX_BORROW_LIMIT = 3
User = get_user_model() # Use Django's configured user model

# --- Custom Permissions ---

class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users (based on UserProfile type)."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.type == 'AD'
        )

class IsAdminOrLibrarian(permissions.BasePermission):
    """Allows access only to admin or librarian users."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.type in ['AD', 'LB']
        )

class IsAdminOrLibrarianOrReadOnly(permissions.BasePermission):
    """
    Allows read access to any authenticated user,
    but write access only to admin or librarian users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions check
        return hasattr(request.user, 'profile') and request.user.profile.type in ['AD', 'LB']

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions check
        return hasattr(request.user, 'profile') and request.user.profile.type in ['AD', 'LB']

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allows access only to the user themselves or an admin user.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        # Admins have access
        if hasattr(request.user, 'profile') and request.user.profile.type == 'AD':
            return True
        # The user themselves has access
        return obj == request.user


# --- Frontend Views ---

def front(request, *args, **kwargs):
    return render(request, 'startpage.html')  # Changed template name


class FrontendAppView(TemplateView):
    template_name = "frontend/index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ============================== #
# 1️ AUTHENTICATION API VIEWS    #
# ============================== #

class RegisterView(generics.CreateAPIView):
    """Handles user registration, creating both User and UserProfile."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] # Anyone can register
    serializer_class = RegisterSerializer

class LoginView(drf_views.APIView):
    """Handles user login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            serializer = UserSerializer(user, context={'request': request}) # Use UserSerializer to return user data
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(drf_views.APIView):
    """Handles user logout."""
    permission_classes = [permissions.IsAuthenticated] # Must be logged in to log out

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

# ============================== #
# 2️ USER MANAGEMENT API VIEWS   #
# ============================== #

class UserListView(generics.ListAPIView):
    """Lists all users (Admin only)."""
    queryset = User.objects.select_related('profile').all() # Optimize query
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Only Admins can list all users

class CurrentUserView(generics.RetrieveAPIView):
    """Gets the profile of the currently authenticated user."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Allows Admins to retrieve, update, or delete a specific user."""
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Only Admins can manage other users
    lookup_field = 'id' # Or 'pk', assuming URL uses user ID

    # Note: Updating UserProfile might need custom logic in the serializer or view
    # if fields like 'type' or 'age' are updated via this endpoint.
    # The current UserSerializer includes read-only profile data.
    # A separate UserProfile update endpoint might be cleaner, or enhance UserSerializer.

class CurrentUserUpdateView(generics.RetrieveUpdateAPIView):
    """Allows the currently authenticated user to view and update their own profile."""
    serializer_class = UserSerializer # Use UserSerializer, potentially enhance it for profile updates
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        # Handle password change - update session hash
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            update_session_auth_hash(self.request, user)

        # Handle profile updates (if UserSerializer is enhanced to accept profile data)
        profile_data = self.request.data.get('profile', {})
        if profile_data and hasattr(user, 'profile'):
            profile_serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True, context={'request': self.request})
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                # Handle profile validation errors if necessary
                # This might require merging errors into the main response
                pass


# ============================== #
# 3️ BOOK MANAGEMENT API VIEWS   #
# ============================== #

class BookListCreateView(generics.ListCreateAPIView):
    """
    Lists all books (paginated, filterable, searchable, orderable).
    Allows authenticated Admin/Librarian users to create new books.
    """
    queryset = Book.objects.select_related('added_by', 'borrower').all() # Optimize query
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrLibrarianOrReadOnly] # Read for any auth user, Create for Admin/Librarian
    filter_backends = DEFAULT_FILTER_BACKENDS
    filterset_fields = ['category', 'language', 'available', 'condition'] # Fields for exact filtering
    search_fields = ['title', 'author', 'isbn'] # Fields for ?search=...
    ordering_fields = ['title', 'author', 'publication_year', 'category'] # Fields for ?ordering=...
    # Add pagination in settings.py for large lists:
    # REST_FRAMEWORK = { 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 10 }

    def perform_create(self, serializer):
        # Automatically set the 'added_by' field to the current user
        serializer.save(added_by=self.request.user)

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific book instance.
    Read access for authenticated users.
    Update/Delete access for Admins/Librarians.
    """
    queryset = Book.objects.select_related('added_by', 'borrower').all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrLibrarianOrReadOnly] # Read for auth, Write for Admin/Librarian
    lookup_field = 'id' # Assuming URL uses book ID

    # perform_update and perform_destroy can be overridden if needed

class BorrowBookView(drf_views.APIView):
    """Handles borrowing a book."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, id=book_id)
        user = request.user

        if not book.available:
            due_date_str = book.due_date.strftime("%Y-%m-%d") if book.due_date else "an unknown date"
            borrower_name = book.borrower.username if book.borrower else "another user"
            return Response(
                {'error': f'Book is currently unavailable. Borrowed by {borrower_name} and due back around {due_date_str}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check borrow limit
        current_borrow_count = Book.objects.filter(borrower=user, available=False).count()
        if current_borrow_count >= MAX_BORROW_LIMIT:
            return Response(
                {'error': f'Borrow limit reached. You cannot borrow more than {MAX_BORROW_LIMIT} books.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrow the book
        book.available = False
        book.borrower = user
        book.borrow_date = date.today()
        book.due_date = date.today() + timedelta(weeks=2) # Standard 2-week loan
        book.save()

        serializer = BookSerializer(book, context={'request': request})
        return Response({'message': 'Book borrowed successfully', 'book': serializer.data}, status=status.HTTP_200_OK)

class ReturnBookView(drf_views.APIView):
    """Handles returning a book."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, id=book_id)
        user = request.user

        if book.available:
            return Response({'error': 'Book is already available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user returning is the one who borrowed it, or if Admin/Librarian is returning
        is_admin_or_librarian = hasattr(user, 'profile') and user.profile.type in ['AD', 'LB']
        if book.borrower != user and not is_admin_or_librarian:
            return Response({'error': 'You did not borrow this book.'}, status=status.HTTP_403_FORBIDDEN)

        # Return the book
        book.available = True
        book.borrower = None
        book.borrow_date = None
        book.due_date = None # Clear due date upon return
        book.save()

        serializer = BookSerializer(book, context={'request': request})
        return Response({'message': 'Book returned successfully', 'book': serializer.data}, status=status.HTTP_200_OK)


class BorrowedBooksListView(drf_views.APIView):
    """
    Lists borrowed books.
    - For regular users: lists books borrowed by them.
    - For Admins/Librarians: lists all borrowed books, grouped by user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        is_admin_or_librarian = hasattr(user, 'profile') and user.profile.type in ['AD', 'LB']
        today = date.today()

        if is_admin_or_librarian:
            # Admins/Librarians see all borrowed books, grouped by borrower
            borrowed_books_query = Book.objects.filter(available=False).select_related('borrower', 'borrower__profile').order_by('borrower__username', 'due_date')
            grouped_books = {}
            for book in borrowed_books_query:
                borrower = book.borrower
                if not borrower: continue # Should not happen if available=False, but safety check

                borrower_name = borrower.username
                if borrower_name not in grouped_books:
                    grouped_books[borrower_name] = {
                        "borrower_id": borrower.id,
                        "borrower_name": borrower_name,
                        "books": []
                    }

                days_left = (book.due_date - today).days if book.due_date else 0
                overdue = days_left < 0
                days_overdue = abs(days_left) if overdue else 0

                book_data = BookSerializer(book, context={'request': request}).data
                # Add calculated fields to the serialized data
                book_data['days_left'] = days_left
                book_data['overdue'] = overdue
                book_data['days_overdue'] = days_overdue
                book_data['due_today'] = days_left == 0

                grouped_books[borrower_name]["books"].append(book_data)

            # Convert dict to list for response
            response_data = list(grouped_books.values())
            return Response({"borrowed_books_by_user": response_data}, status=status.HTTP_200_OK)

        else:
            # Regular users see only their borrowed books
            user_borrowed_books = Book.objects.filter(borrower=user, available=False).select_related('borrower', 'borrower__profile').order_by('due_date')

            book_list = []
            for book in user_borrowed_books:
                days_left = (book.due_date - today).days if book.due_date else 0
                overdue = days_left < 0
                days_overdue = abs(days_left) if overdue else 0

                book_data = BookSerializer(book, context={'request': request}).data
                book_data['days_left'] = days_left
                book_data['overdue'] = overdue
                book_data['days_overdue'] = days_overdue
                book_data['due_today'] = days_left == 0
                book_list.append(book_data)

            return Response({"my_borrowed_books": book_list}, status=status.HTTP_200_OK)


# ============================== #
# 4️ SECURITY & CSRF API VIEWS   #
# ============================== #

@api_view(['GET'])
@drf_permission_classes([permissions.AllowAny]) # Anyone can get the CSRF token
def csrf_token_view(request):
    """Provides the CSRF token needed for authenticated POST/PUT/DELETE requests."""
    return Response({"csrfToken": get_token(request)})

# Note: The old `validations.py` functions are generally superseded by serializer validation.
# If specific complex validations were needed outside a serializer context, they could remain,
# but standard field validation belongs in serializers.