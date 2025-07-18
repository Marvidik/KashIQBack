from rest_framework.response import Response
from .models import UserIds
from rest_framework import status
import requests
import threading
import time
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os

# Load the .env file into environment variables
load_dotenv()
MONO=os.getenv("MONO")

def fetch_and_save_bank_name(account_id, user_id):
    url = f"https://api.withmono.com/v2/accounts/{account_id}"
    headers = { "mono-sec-key": MONO }

    try:
        response = requests.get(url, headers=headers)
        time.sleep(1)
        if response.status_code == 200:
            data = response.json()
            bank_name= data['data']['account']['institution']['name']

            if bank_name:
                user = User.objects.get(id=user_id)
                UserIds.objects.update_or_create(
                    user=user,
                    monoid=account_id,
                    defaults={"bank": bank_name}
                )

    except Exception as e:
        print("❌ Error in background thread:", str(e))

def run_async_bank_fetch(account_id, user):
    threading.Thread(target=fetch_and_save_bank_name, args=(account_id, user.id)).start()

