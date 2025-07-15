# views.py
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserIds
from rest_framework import status
from .utils import fetch_and_save_bank_name,run_async_bank_fetch

MONO_SECRET_KEY = "j"
MONO="jhjh"

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def exchange_code(request):
    code = request.data.get("code")

    if not code:
        return Response({"error": "Missing code"}, status=status.HTTP_400_BAD_REQUEST)

    url = "https://api.withmono.com/account/auth"
    headers = {
        "mono-sec-key": MONO
    }
    data = { "code": code }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response.status_code == 200:
        monoid = response_data.get("id")  # or response_data["id"]
        if monoid:
            UserIds.objects.create(
                user=request.user,
                monoid= monoid
            )

    # Step 3: Immediately fetch bank name and update it
    run_async_bank_fetch(monoid, request.user)
    return Response(response_data, status=response.status_code)


@csrf_exempt
def get_account_details(request, account_id):
    url = f"https://api.withmono.com/accounts/{account_id}"
    headers = {
        "mono-sec-key": MONO_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), status=response.status_code)



@csrf_exempt
def get_account_transactions(request, account_id):
    url = f"https://api.withmono.com/accounts/{account_id}/transactions"
    headers = {
        "mono-sec-key": MONO_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), status=response.status_code)
