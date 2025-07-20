# serializers.py
from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['user','id','acct_name','bank','type','balance','acct_number']
