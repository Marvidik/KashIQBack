# users/urls.py
from django.urls import path
from .views import login,register

urlpatterns = [
    path('login/', login, name='email-login'),
    path('register/',register,name="register")
]
