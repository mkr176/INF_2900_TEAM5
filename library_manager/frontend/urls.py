from django.urls import path
from .views import front

app_name = 'frontend'

urlpatterns = [
    path('', front, name='front'),
]
