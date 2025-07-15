from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserIds(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    monoid=models.CharField(max_length=100)
    bank=models.CharField(max_length=50, default="")


    def __str__(self):

        return self.bank
