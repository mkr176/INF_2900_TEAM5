from django.urls import path
from .views import front
from .views import front, RegisterView, LoginView, LogoutView

app_name = 'frontend'

urlpatterns = [
    path('', front, name='front'),
    
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
