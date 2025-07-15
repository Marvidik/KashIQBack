from rest_framework.response import Response
from .models import UserIds
from rest_framework import status
import requests
import threading
import time
from django.contrib.auth.models import User


MONO_SECRET_KEY = "test_sk_rvht2igf140hru6jr64l"
MONO="test_sk_lirnp3ijq9eq5s8yjfqj"

def fetch_and_save_bank_name(account_id, user_id):
    print("🔥 Background task started for account_id:", account_id)

    url = f"https://api.withmono.com/accounts/{account_id}"
    headers = { "mono-sec-key": MONO }

    try:
        print("➡️ Sending request to Mono...")
        response = requests.get(url, headers=headers)
        print("⬅️ Got response from Mono")
        print("🌐 Fetched account info:", response.status_code)

        time.sleep(1)
        if response.status_code == 504:
            print("⚠️ Mono API timed out. Will not update DB.")
            return
        if response.status_code == 200:
            print("again")
            data = response.json()
            bank_name = data.get("institution", {}).get("name")
            print("🏦 Bank name:", bank_name)

            if bank_name:
                print("here")
                user = User.objects.get(id=user_id)
                UserIds.objects.update_or_create(
                    user=user,
                    monoid=account_id,
                    defaults={"bank": bank_name}
                )
                print("✅ Bank name saved to DB")

    except Exception as e:
        print("❌ Error in background thread:", str(e))



def run_async_bank_fetch(account_id, user):
    threading.Thread(target=fetch_and_save_bank_name, args=(account_id, user.id)).start()

