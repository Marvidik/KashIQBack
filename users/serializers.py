from rest_framework import serializers
from .models import CustomerDetails, SpendingLimit

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

class SpendingLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingLimit
        fields = ['id', 'user', 'month', 'limit_amount']
        read_only_fields = ['user']

    def validate_limit_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Limit amount is required.")
        if value < 0:
            raise serializers.ValidationError("Limit amount must be non-negative.")
        return value

    def validate_month(self, value):
        # Ensure month is the first day of the month
        return value.replace(day=1)
