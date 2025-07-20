# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mono.models import Account,Transaction
from mono.serializers import AccountSerializer
from .models import CustomerDetails
from .serializers import CustomerDetailsSerializer
from rest_framework import status
from mono.transaction_analysis import *

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

    if account_id:
        transactions = Transaction.objects.filter(account__id=account_id, account__user=user)
    else:
        transactions = Transaction.objects.filter(account__user=user)

    result = top_transactions(transactions, count)
    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_credit_debit_summary(request):
    user = request.user
    account_id = request.query_params.get("account_id")

    if account_id:
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        transactions = Transaction.objects.filter(account=account)
    else:
        transactions = Transaction.objects.filter(account__user=user)

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
    if account_id:
        transactions = Transaction.objects.filter(account_id=account_id, account__user=request.user)
    else:
        transactions = Transaction.objects.filter(account__user=request.user)

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
