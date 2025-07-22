# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mono.models import Account,Transaction
from mono.serializers import AccountSerializer
from .models import CustomerDetails,SpendingLimit
from .serializers import CustomerDetailsSerializer,SpendingLimitSerializer
from rest_framework import status
from mono.transaction_analysis import *
from datetime import datetime
from .utils import check_if_spending_exceeds_limit

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_accounts(request):
    accounts = Account.objects.filter(user=request.user)
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_details(request):
    try:
        customer = CustomerDetails.objects.get(user=request.user)
    except CustomerDetails.DoesNotExist:
        return Response({"detail": "Customer details not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomerDetailsSerializer(customer)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_top_transactions_view(request):
    user = request.user
    count = int(request.query_params.get('count', 5))
    account_id = request.query_params.get('account_id')
    mlnth = request.query_params.get('mlnth')  # format: YYYY-MM
    day = request.query_params.get('day')      # format: YYYY-MM-DD

    if account_id:
        transactions = Transaction.objects.filter(account__id=account_id, account__user=user)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    # Filter by month (mlnth = 'YYYY-MM')
    if mlnth:
        try:
            year, month = map(int, mlnth.split('-'))
            transactions = transactions.filter(date__year=year, date__month=month)
        except ValueError:
            return Response({'error': 'Invalid "mlnth" format. Use YYYY-MM'}, status=400)

    # Filter by specific day (day = 'YYYY-MM-DD')
    elif day:
        try:
            day_obj = datetime.strptime(day, '%Y-%m-%d')
            transactions = transactions.filter(
                date__year=day_obj.year,
                date__month=day_obj.month,
                date__day=day_obj.day
            )
        except ValueError:
            return Response({'error': 'Invalid "day" format. Use YYYY-MM-DD'}, status=400)

    result = top_transactions(transactions, count)
    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_credit_debit_summary(request):
    user = request.user
    account_id = request.query_params.get("account_id")
    mlnth = request.query_params.get("mlnth")  # format: YYYY-MM
    day = request.query_params.get("day")      # format: YYYY-MM-DD

    if account_id:
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        transactions = Transaction.objects.filter(account=account)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    # Apply month filter
    if mlnth:
        try:
            year, month = map(int, mlnth.split("-"))
            transactions = transactions.filter(date__year=year, date__month=month)
        except ValueError:
            return Response({"error": 'Invalid "mlnth" format. Use YYYY-MM'}, status=400)

    # Apply day filter
    elif day:
        try:
            day_obj = datetime.strptime(day, "%Y-%m-%d")
            transactions = transactions.filter(
                date__year=day_obj.year,
                date__month=day_obj.month,
                date__day=day_obj.day
            )
        except ValueError:
            return Response({"error": 'Invalid "day" format. Use YYYY-MM-DD'}, status=400)

    result = calculate_total_credits_and_debits(transactions)
    return Response(result)

@api_view(['GET'])
def monthly_breakdown(request, account_id=None):
    user = request.user

    if account_id:
        try:
            account = Account.objects.get(id=account_id, user=user)
            transactions = Transaction.objects.filter(account=account)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=404)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    data = get_monthly_breakdown(transactions)
    return Response({"monthly_breakdown": data})



@api_view(['GET'])
def category_summary(request, account_id=None):
    user = request.user

    if account_id:
        try:
            account = Account.objects.get(id=account_id, user=user)
            transactions = Transaction.objects.filter(account=account)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=404)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    data = get_category_summary(transactions)
    return Response({"category_summary": data})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_spending_categories(request, account_id=None):
    user = request.user
    mlnth = request.query_params.get("mlnth")  # format: YYYY-MM
    day = request.query_params.get("day")      # format: YYYY-MM-DD

    if account_id:
        transactions = Transaction.objects.filter(account_id=account_id, account__user=user)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    # Apply month filter
    if mlnth:
        try:
            year, month = map(int, mlnth.split("-"))
            transactions = transactions.filter(date__year=year, date__month=month)
        except ValueError:
            return Response({"error": 'Invalid "mlnth" format. Use YYYY-MM'}, status=400)

    # Apply day filter
    elif day:
        try:
            day_obj = datetime.strptime(day, "%Y-%m-%d")
            transactions = transactions.filter(
                date__year=day_obj.year,
                date__month=day_obj.month,
                date__day=day_obj.day
            )
        except ValueError:
            return Response({"error": 'Invalid "day" format. Use YYYY-MM-DD'}, status=400)

    top_categories = get_top_spending_categories(transactions)
    return Response({"top_categories": top_categories})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recurring_payments_view(request, account_id=None):
    if account_id:
        transactions = Transaction.objects.filter(account_id=account_id, account__user=request.user)
    else:
        transactions = Transaction.objects.filter(account__user=request.user)

    if not transactions.exists():
        return Response({"message": "No transactions found."}, status=404)

    recurring = detect_recurring_payments(transactions)

    return Response({
        "recurring_payments": recurring
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_spending_limit(request):
    user = request.user
    data = request.data.copy()
    month = data.get('month')
    limit = data.get('limit_amount')

    # Validate month format
    try:
        month_date = datetime.strptime(month, '%Y-%m').date()
        month_date = month_date.replace(day=1)
    except (ValueError, TypeError):
        return Response({"error": "Invalid month format. Use YYYY-MM"}, status=400)

    data['month'] = month_date
    data['user'] = user.id

    # Check if user has already exceeded the new limit for the month
    exceeded, spent, error = check_if_spending_exceeds_limit(user, month_date.year, month_date.month, limit)
    if error:
        return Response({"error": error}, status=400)
    if exceeded:
        return Response({
            "error": "You have already spent more than the limit you are trying to set for this month.",
            "spent": spent,
            "limit_attempted": limit
        }, status=400)

    # Check if SpendingLimit exists for user/month
    try:
        instance = SpendingLimit.objects.get(user=user, month=month_date)
        serializer = SpendingLimitSerializer(instance, data=data, partial=True)
    except SpendingLimit.DoesNotExist:
        serializer = SpendingLimitSerializer(data=data)

    if serializer.is_valid():
        serializer.save(user=user)
        return Response({"message": "Spending limit set", "limit": serializer.data['limit_amount'], "spending_limit": serializer.data})
    else:
        return Response(serializer.errors, status=400)