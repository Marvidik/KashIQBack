from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Account(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    monoid=models.CharField(max_length=100)
    acct_name=models.CharField(max_length=100,null=True,blank=True)
    bank=models.CharField(max_length=50, default="")
    type=models.CharField(max_length=50)
    balance=models.CharField(max_length=50)
    acct_number=models.CharField(max_length=13,null=True,blank=True)
    response = models.JSONField(blank=True,null=True)
    linked_on=models.DateTimeField(auto_now_add=True)



    def __str__(self):

        return self.user.username + " " +  self.bank
    


