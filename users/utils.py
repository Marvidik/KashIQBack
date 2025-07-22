from django.db.models import Sum
from .models import SpendingLimit
from mono.models import Transaction
from datetime import date

def check_if_limit_exceeded(user, year, month):
    # Total spent by user that month
    total_spent = Transaction.objects.filter(
        account__user=user,
        type="debit",
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Get the limit
    limit = SpendingLimit.objects.filter(
        user=user,
        month__year=year,
        month__month=month
    ).first()

    if limit:
        exceeded = total_spent > limit.limit_amount
        return {
            "limit": float(limit.limit_amount),
            "spent": float(total_spent),
            "exceeded": exceeded
        }
    return {
        "limit": None,
        "spent": float(total_spent),
        "exceeded": False
    }


def check_if_spending_exceeds_limit(user, year, month, new_limit):
    """
    Returns a tuple (exceeded, spent, error):
    - exceeded: True if user's spending for the month exceeds the new_limit
    - spent: total spent
    - error: error message if trying to set for a previous month, else None
    """
    today = date.today()
    # Only allow setting for current or future months
    if year < today.year or (year == today.year and month < today.month):
        return None, None, "Cannot set limit for a previous month."
    info = check_if_limit_exceeded(user, year, month)
    try:
        new_limit_val = float(new_limit)
    except (TypeError, ValueError):
        return None, None, "Limit must be a valid number."
    return info['spent'] > new_limit_val, info['spent'], None
