from rest_framework import serializers
from .models import CustomerDetails

class CustomerDetailsSerializer(serializers.ModelSerializer):
    bvn = serializers.ReadOnlyField()

    class Meta:
        model = CustomerDetails
        fields = [
            'full_name',
            'email',
            'phone',
            'gender',
            'address_line1',
            'address_line2',
            'marital_status',
            'verified',
            'created_at',
            'updated_at',
            'bvn',
        ]
