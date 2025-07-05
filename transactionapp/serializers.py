from rest_framework import serializers
from .models import Transaction_Model

class TransactionSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%b %d, %Y - %I:%M %p")
    class Meta:
        model = Transaction_Model
        fields = '__all__'  # You can also specify selected fields like ['id', 'username', 'amount', 'transaction_type']
