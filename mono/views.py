# views.py
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Account
from rest_framework import status
from .utils import fetch_and_save_bank_name,run_async_bank_fetch,run_async_details_fetch
from dotenv import load_dotenv
import os
import json

# Load the .env file into environment variables
load_dotenv()
MONO=os.getenv("MONO")

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def exchange_code(request):
    code = request.data.get("code")

    if not code:
        return Response({"error": "Missing code"}, status=status.HTTP_400_BAD_REQUEST)

    url = "https://api.withmono.com/v2/accounts/auth"
    headers = {
        "mono-sec-key": MONO
    }
    data = { "code": code }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response.status_code == 200:
        monoid = response_data['data']['id']
        if monoid:
            run_async_bank_fetch(monoid, request.user)
            run_async_details_fetch(monoid, request.user)
    return Response(response_data, status=response.status_code)


@csrf_exempt
def get_account_details(request, account_id):
    url = f"https://api.withmono.com/v2/accounts/{account_id}"
    headers = {
        "mono-sec-key": MONO,
    }

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), status=response.status_code)



@csrf_exempt
def get_account_transactions(request, account_id):
    url = f"https://api.withmono.com/v2/accounts/{account_id}/transactions?paginate=false"
    headers = {
        "mono-sec-key": MONO
    }

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), status=response.status_code)



@csrf_exempt
def categorize_transactions(request, account_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))  # Parse JSON body
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        # Validate required fields
        transactions = data.get("transactions")
        category = data.get("category")

        if not transactions or not category:
            return JsonResponse({"error": "Missing 'transactions' or 'category' field"}, status=400)

        # Mono API request
        url = f"https://api.withmono.com/v2/accounts/{account_id}/transactions/categorise"
        headers = {
            "mono-sec-key": MONO,
            "Content-Type": "application/json"
        }
        payload = {
            "transactions": transactions,  # List of transaction IDs
            "category": category
        }

        response = requests.post(url, headers=headers, json=payload)
        return JsonResponse(response.json(), status=response.status_code)

    return JsonResponse({"error": "Invalid request method"}, status=405)
