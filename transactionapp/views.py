from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction_Model
from django.contrib.auth import get_user_model
from .serializers import TransactionSerializer
from bankingapp.models import BankAccount  # Import BankAccount model

user = get_user_model()

@api_view(['POST'])
def transaction_history(request):
    username = request.data.get('username')

    if not username:
        return Response({'message': "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get the user instance
        cleaned_username = username.strip().strip('"')
        user_instance = user.objects.get(username=cleaned_username)
    except user.DoesNotExist:
        return Response({'message': "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get all bank accounts associated with the user
    accounts = BankAccount.objects.filter(user=user_instance)
    
    # Get transactions linked to these accounts
    transactions = Transaction_Model.objects.filter(account__in=accounts)

    if not transactions.exists():
        return Response({'message': "No transactions found for this user"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the transactions
    serialized_data = TransactionSerializer(transactions, many=True).data
    return Response({'data': serialized_data}, status=status.HTTP_200_OK)