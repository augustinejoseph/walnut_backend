from rest_framework import serializers
from .models import Transaction


class TransactionCreateSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    source_account = serializers.CharField()
    destination_account = serializers.CharField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    currency = serializers.CharField()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
