from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Account(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    monoid=models.CharField(max_length=100)
    acct_name=models.CharField("Account Name",max_length=100,null=True,blank=True)
    bank=models.CharField("Bank Name",max_length=50, default="")
    type=models.CharField(max_length=50)
    balance=models.CharField(max_length=50)
    acct_number=models.CharField("Account Number",max_length=13,null=True,blank=True)
    response = models.JSONField(blank=True,null=True)
    linked_on=models.DateTimeField(auto_now_add=True)



    def __str__(self):

        return self.user.username + " " +  self.bank
    

class Transaction(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    txn_id = models.CharField(max_length=100, unique=True)  # Mono's unique transaction ID
    amount = models.FloatField()
    type = models.CharField(max_length=20)  # 'debit' or 'credit'
    narration = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    category = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=10, default="NGN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_id} - {self.amount}"


