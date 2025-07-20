# users/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("accounts/", user_accounts,name="List-all-user-accounts"),
    path("profile/", get_customer_details,name="List-user-accounts-details"),
    path('analyze-top-transactions/', analyze_top_transactions_view, name='analyze-transactions'),
    path('debit-credit/',get_credit_debit_summary,name="debit-credit"),
    path('monthly-breakdown/<int:account_id>/',monthly_breakdown,name="monthly-breakdown"),
    path('monthly-breakdown/', monthly_breakdown),

    path('category-summary/', category_summary),
    path('category-summary/<int:account_id>/', category_summary),

    path("top-categories/", top_spending_categories),
    path("top-categories/<int:account_id>/", top_spending_categories),

    path('recurring-payments/', recurring_payments_view),
    path('recurring-payments/<int:account_id>/', recurring_payments_view),



    
]
