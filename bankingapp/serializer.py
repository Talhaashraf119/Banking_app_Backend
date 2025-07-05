from rest_framework import serializers
from .models import BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model=BankAccount
        fields = '__all__'