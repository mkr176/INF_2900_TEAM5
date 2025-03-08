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
from .views import RegisterView, LoginView, LogoutView, ListUsersView, ListBooksView
from django.views.generic.base import RedirectView

app_name = "frontend"

favicon_view = RedirectView.as_view(url="/static/favicon.ico", permanent=True)

urlpatterns = [
    path("api/signup/", RegisterView.as_view(), name="signup"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    re_path(r"^favicon\.ico$", favicon_view),
    # Catch-all for React routing
    re_path(
        r"^(?!api/).*$",
        TemplateView.as_view(template_name="startpage.html"),
        name="index",
    ),  # Name the index view
    path("api/users/", ListUsersView.as_view(), name="list-users"),
    path("api/books/", ListBooksView.as_view(), name="list-books")
]
