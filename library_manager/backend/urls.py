"""
URL configuration for backend project.
"""
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

# Import the new DRF views
from .views import (
    # Frontend
    # front, <--- REMOVE THIS LINE
    FrontendAppView,
    # Auth
    RegisterView, LoginView, LogoutView,
    # User Management
    UserListView, CurrentUserView, UserDetailView, CurrentUserUpdateView, promote_user_to_librarian,
    # Book Management
    BookListCreateView, BookDetailView, BorrowBookView, ReturnBookView, BorrowedBooksListView,
    # Security & CSRF
    csrf_token_view,
)

app_name = "backend" # Changed app_name to 'backend' as it contains the API logic

favicon_view = RedirectView.as_view(url="/static/favicon.ico", permanent=True)

urlpatterns = [
    # ============================== #
    # 1️ AUTHENTICATION ROUTES        #
    # ============================== #
    path("api/auth/register/", RegisterView.as_view(), name="register"), # Changed from signup
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),

    # ============================== #
    # 2️ USER MANAGEMENT ROUTES       #
    # ============================== #
    # List all users (Admin only)
    path("api/users/", UserListView.as_view(), name="user-list"),
    # Get details of the currently logged-in user
    path("api/users/me/", CurrentUserView.as_view(), name="current-user"),
    # Update details of the currently logged-in user
    path("api/users/me/update/", CurrentUserUpdateView.as_view(), name="current-user-update"), # Changed from update-profile
    # Retrieve, Update, Delete a specific user by ID (Admin only)
    path("api/users/<int:id>/", UserDetailView.as_view(), name="user-detail"), # Use 'id' consistent with view lookup_field
    #promote the user to librarian (Admin only)
    path("api/users/<int:user_id>/promote/", promote_user_to_librarian, name="user-promote"), # Use 'id' consistent with view lookup_field
    # --- Removed old/redundant user routes ---
    # path("api/user/", get_user_info), # Replaced by current-user
    # path("api/user/<int:user_id>/", UserProfileView.as_view(), name="user-profile"), # Replaced by user-detail or current-user
    # path("api/user/<int:user_id>/update/", UpdateUserProfileView.as_view(), name="update-user-profile"), # Replaced by user-detail
    # path("api/update-profile/", update_profile, name="update-profile"), # Replaced by current-user-update
    # path("api/create_users/", CreateUserView.as_view(), name="create-users"), # Replaced by register or user-list (POST) if needed
    # path("api/user/<int:user_id>/delete/", DeleteUserView.as_view(), name="delete-user"), # Replaced by user-detail (DELETE)

    # ============================== #
    # 3️ BOOK MANAGEMENT ROUTES       #
    # ============================== #
    # List books (GET) and Create books (POST)
    path("api/books/", BookListCreateView.as_view(), name="book-list-create"),
    # Retrieve (GET), Update (PUT/PATCH), Delete (DELETE) a specific book
    path("api/books/<int:id>/", BookDetailView.as_view(), name="book-detail"), # Use 'id' consistent with view lookup_field
    # Borrow a specific book (POST)
    path("api/books/<int:book_id>/borrow/", BorrowBookView.as_view(), name="book-borrow"),
    # Return a specific book (POST)
    path("api/books/<int:book_id>/return/", ReturnBookView.as_view(), name="book-return"),
    # List borrowed books (for current user or all users for admin/librarian)
    path("api/books/borrowed/", BorrowedBooksListView.as_view(), name="borrowed-books-list"),

    # --- Removed old/redundant book routes ---
    # path("api/principal/", ListBooksView.as_view(), name="list-books"), # Combined into book-list-create
    # path("api/create_book/", CreateBookView.as_view(), name="create-book"), # Combined into book-list-create
    # path("api/book/<int:book_id>/", DeleteBookView.as_view(), name="delete-book"), # Combined into book-detail (DELETE)
    # path("api/borrow_book/", BorrowBookView.as_view(), name="borrow-book"), # Replaced by book-borrow/<id>
    # path("api/update_book/<int:book_id>/", UpdateBookView.as_view(), name="update-book"), # Combined into book-detail (PUT/PATCH)
    # path("api/book/<int:book_id>/", BookDetailView.as_view(), name="book-detail"), # Kept similar structure
    # path("api/borrowed_books/", BorrowedBooksView.as_view(), name="borrowed-books"), # Replaced by borrowed-books-list

    # ============================== #
    # 4️ SECURITY & CSRF ROUTES       #
    # ============================== #
    path("api/csrf/", csrf_token_view, name="csrf-token"), # Renamed for clarity

    # ============================== #
    # 5️ STATIC & FRONTEND ROUTES     #
    # ============================== #
    re_path(r"^favicon\.ico$", favicon_view),
    # Catch-all for frontend routing (ensure it's the last pattern)
    # It serves 'startpage.html' for any path not starting with 'api/'
    re_path(
        r"^(?!api/).*$",
        # Use the 'front' function view or FrontendAppView class view
        # front, # Option 1: Use the function view
        FrontendAppView.as_view(template_name="startpage.html"), # Option 2: Use the class view (adjust template name if needed)
        name="index",
    ),  # Catch-all for React routing
]
