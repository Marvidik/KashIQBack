from .models import Account
import requests
import threading
import time
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os
from users.models import CustomerDetails
from datetime import datetime
from django.conf import settings
from cryptography.fernet import Fernet

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
            account_type=data['data']['account']['type']
            balance=data['data']['account']['balance']
            acct_number=data['data']['account']['account_number']
            acct_name=data['data']['account']['name']
            

            if bank_name:
                user = User.objects.get(id=user_id)

                try:
                    # Check if the account with the same acct_number already exists
                    account = Account.objects.get(acct_number=acct_number,bank=bank_name)

                    # If found, just update the monoid
                    account.monoid = account_id
                    account.response=data
                    account.save(update_fields=['monoid', 'response'])

                except Account.DoesNotExist:
                    # Else, create new account with full details
                    Account.objects.create(
                        user=user,
                        monoid=account_id,
                        bank=bank_name,
                        type=account_type,
                        balance=balance,
                        response=data,
                        acct_number=acct_number,
                        acct_name=acct_name
                    )

    except Exception as e:
        print("❌ Error in background thread:", str(e))

def run_async_bank_fetch(account_id, user):
    threading.Thread(target=fetch_and_save_bank_name, args=(account_id, user.id)).start()



def fetch_and_save_bank_details(account_id, user_id):
    url = f"https://api.withmono.com/v2/accounts/{account_id}/identity"
    headers = { "mono-sec-key": MONO }

    try:
        response = requests.get(url, headers=headers)
        print("Started")
        if response.status_code == 200:
            data = response.json()
            user = User.objects.get(id=user_id)
            if not CustomerDetails.objects.filter(user=user).exists():
                f = Fernet(settings.FERNET_KEY)
                encrypted_bvn = f.encrypt(data['data']["bvn"].encode()).decode()
                CustomerDetails.objects.get_or_create(
                    user=user,
                    defaults={
                        "full_name": data['data']["full_name"],
                        "email": data['data']["email"],
                        "_bvn": encrypted_bvn,
                        "phone": data['data']["phone"],
                        "gender": data['data']["gender"],
                        "address_line1": data['data']["address_line1"],
                        "address_line2": data['data']["address_line2"],
                        "marital_status": data['data']["marital_status"],
                        "verified": True,  # optional 
                        "created_at": datetime.fromisoformat(data['data']["created_at"].replace("Z", "+00:00")),
                        "updated_at": datetime.fromisoformat(data['data']["updated_at"].replace("Z", "+00:00")),
                    }
                )
            print(data)

    except Exception as e:
        print("❌ Error in background thread:", str(e))

def run_async_details_fetch(account_id, user):
    if not CustomerDetails.objects.filter(user=user).exists():
        threading.Thread(target=fetch_and_save_bank_details, args=(account_id, user.id)).start()
