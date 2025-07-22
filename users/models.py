from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
# Create your models here.


class CustomerDetails(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)  # newly added
    _bvn = models.CharField(max_length=11, unique=True,null=True, blank=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, null=True, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)  # newly added
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    @property
    def bvn(self):
        f = Fernet(settings.FERNET_KEY)
        try:
            return f.decrypt(self._bvn.encode()).decode()
        except:
            return None

    @bvn.setter
    def bvn(self, value):
        self._bvn = value  # Will be encrypted in save()

    def __str__(self):
        return f"{self.full_name} (BVN: {self._bvn})"
    

    def save(self, *args, **kwargs):
            if self._bvn and not self._bvn.startswith("gAAAA"):  # crude check to avoid double encryption
                f = Fernet(settings.FERNET_KEY)
                self._bvn = f.encrypt(self._bvn.encode()).decode()
            super().save(*args, **kwargs)



class SpendingLimit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # Just use the first day of the month
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('user', 'month')

    def clean(self):
        if self.limit_amount is None:
            raise ValidationError("Limit amount is required.")
        if self.limit_amount < 0:
            raise ValidationError("Limit amount must be non-negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%Y-%m')} - {self.limit_amount}"