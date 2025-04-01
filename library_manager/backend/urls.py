"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from django.views.generic import TemplateView
from .views import( 
    RegisterView, LoginView, LogoutView, ListUsersView, 
    UserProfileView, CurrentUserView,  CreateUserView, UpdateUserProfileView, DeleteUserView,
    ListBooksView, BorrowBookView, CreateBookView, DeleteBookView, UpdateBookView, BookDetailView, BorrowedBooksView,
    csrf_token_view, 
    get_user_info, update_profile
)

from django.views.generic.base import RedirectView

app_name = "frontend"

favicon_view = RedirectView.as_view(url="/static/favicon.ico", permanent=True)

urlpatterns = [
    # ============================== #
    # 1️ AUTHENTICATION ROUTES        #
    # ============================== #
    path("api/signup/", RegisterView.as_view(), name="signup"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),

    
    # ============================== #
    # 2️ USER MANAGEMENT ROUTES       #
    # ============================== #
    path("api/users/", ListUsersView.as_view(), name="list-users"),
    path("api/current_user/", CurrentUserView.as_view(), name="current-user"),
    path("api/user/", get_user_info),
    path("api/user/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("api/user/<int:user_id>/update/", UpdateUserProfileView.as_view(), name="update-user-profile"),
    path("api/update-profile/", update_profile, name="update-profile"),
    path("api/create_users/", CreateUserView.as_view(), name="create-users"),
    path("api/user/<int:user_id>/delete/", DeleteUserView.as_view(), name="delete-user"),



    # ============================== #
    # 3️ BOOK MANAGEMENT ROUTES       #
    # ============================== #

    path("api/principal/", ListBooksView.as_view(), name="list-books"),  
    path("api/books/", ListBooksView.as_view(), name="list-books"),
    path("api/create_book/", CreateBookView.as_view(), name="create-book"),
    path("api/book/<int:book_id>/", DeleteBookView.as_view(), name="delete-book"), # Corrected URL for delete book
    path("api/borrow_book/", BorrowBookView.as_view(), name="borrow-book"),
    path("api/update_book/<int:book_id>/", UpdateBookView.as_view(), name="update-book"),
    path("api/book/<int:book_id>/", BookDetailView.as_view(), name="book-detail"),
    path("api/borrowed_books/", BorrowedBooksView.as_view(), name="borrowed-books"),


    # ============================== #
    # 4️ SECURITY & CSRF ROUTES       #
    # ============================== #
    path("api/csrf/", csrf_token_view),


    # ============================== #
    # 5️ STATIC & FRONTEND ROUTES     #
    # ============================== #


    re_path(r"^favicon\.ico$", favicon_view),
    re_path(
        r"^(?!api/).*$",
        TemplateView.as_view(template_name="startpage.html"),
        name="index",
    ),  # Catch-all for React routing
]
