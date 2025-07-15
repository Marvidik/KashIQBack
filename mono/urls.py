# users/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("exchange-code/", exchange_code),
    path("account/<str:account_id>/", get_account_details),
    path("account/<str:account_id>/transactions/", get_account_transactions),
]
