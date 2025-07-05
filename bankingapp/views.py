from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password,check_password
from .models import BankAccount
import random
from decimal import Decimal,InvalidOperation
from transactionapp.models import Transaction_Model
from .serializer import BankAccountSerializer


User = get_user_model()  # Custom user model

@api_view(['POST'])
def create_account(request):
    try:
        username = request.data.get('username')
        image = request.FILES.get('image')
        account_type = request.data.get('account_type', 'savings')
        date_of_birth = request.data.get('date_of_birth')
        national_id = request.data.get('national_id')
        address = request.data.get('address')
        occupation = request.data.get('occupation', "")
        monthly_income = request.data.get('monthly_income', 0.00)
        tax_id = request.data.get('tax_id', None)
        initial_deposit = request.data.get('initial_deposit', 0.00)
        transaction_pin = request.data.get('transaction_pin')
        security_question = request.data.get('security_question')
        security_answer = request.data.get('security_answer')

        # Validate required fields
        required_fields = [
            username, image, date_of_birth, 
            national_id, address, transaction_pin,
            security_question, security_answer
        ]
        if not all(required_fields):
            return Response(
                {'message': "All required fields must be filled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'message': 'User does not exist.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already has a bank account
        if BankAccount.objects.filter(user=user).exists():
            return Response(
                {'message': 'User already has a bank account.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique 12-digit account number
        while True:
            account_number = str(random.randint(10**11, 10**12 - 1))  # 12 digits
            if not BankAccount.objects.filter(account_number=account_number).exists():
                break

        # Create bank account
        BankAccount.objects.create(
            user=user,
            image=image,
            account_number=account_number,
            account_type=account_type,
            phone_number=request.data.get('phone_number'),  # Ensure user model has a `phone` field
            email=user.email,
            address=address,
            date_of_birth=date_of_birth,
            national_id=national_id,
            occupation=occupation,
            monthly_income=monthly_income,
            tax_id=tax_id,
            initial_deposit=initial_deposit,
            transaction_pin=make_password(transaction_pin),  # Hash PIN
            security_question=security_question,
            security_answer=security_answer,
        )

        return Response(
            {'message': 'Account created successfully!', 'account_number': account_number}, 
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
def show_info(request):
    try:
        username = request.data.get('username')  # Get username from request body
        print("Received username:", username)

        if not username:
            return Response({'message': 'Username is required!'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user instance from the User model
        cleaned_username = username.strip().strip('"')
        user = User.objects.filter(username__iexact=cleaned_username).first()

        if not user:  # Check if user exists
            return Response({'message': 'User does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        # Get the associated bank account
        bank_account = BankAccount.objects.filter(user=user).first()

        if not bank_account:
            return Response({'message': 'Bank account does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        # Construct the response data
        # user_data = {
        #     "username": user.username,
        #     "email": user.email,
        #     "phone": user.phone,
        #     "account_number": bank_account.account_number,
        #     "account_type": bank_account.account_type,
        #     "balance": bank_account.initial_deposit,
        #     "created_at": bank_account.created_at,
        #     "profile_image": bank_account.image.url if bank_account.image else None,
        # }
        serializedata=BankAccountSerializer(bank_account).data

        return Response({'data': serializedata}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def Withdraw_money(request):
    account_number = request.data.get('account_number')
    withdraw_amount = request.data.get('draw_amount')  # Ensure key matches frontend
    transaction_pin = request.data.get('transaction_pin')

    # Validate required fields
    if not all([account_number, withdraw_amount, transaction_pin]):
        return Response(
            {'message': "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate withdrawal amount type
    try:
        withdraw_amount = Decimal(withdraw_amount)
        if withdraw_amount <= 0:
            raise ValueError
    except (TypeError, ValueError, InvalidOperation):
        return Response(
            {'message': "Invalid withdrawal amount."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch account
    account = BankAccount.objects.filter(account_number=account_number).first()
    if not account:
        return Response(
            {'message': "Account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Validate PIN
    if not check_password(transaction_pin, account.transaction_pin):
        return Response(
            {'message': "Incorrect PIN."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check balance
    if withdraw_amount > account.initial_deposit:  # Use `balance`, not `initial_deposit`
        return Response(
            {'message': "Insufficient funds."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update balance
    account.initial_deposit -= withdraw_amount
    account.save()

    transaction_id = str(random.randint(10**9, 10**10 - 1))  # 10-digit ID
    reference_number = str(random.randint(10**7, 10**8 - 1))
    Transaction_Model.objects.create(
        account=account,
        transaction_type="withdrawal",
        amount=withdraw_amount,
        transaction_id=transaction_id,
        reference_number=reference_number,
        status='completed',
        post_balance=account.initial_deposit
    )

    return Response(
        {
            'message': "Amount withdrawn successfully.",
            'remaining_balance': account.initial_deposit
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def Add_money(request):
    account_number = request.data.get('account_number')
    add_amount = request.data.get('add_amount')  # Ensure key matches frontend
    transaction_pin = request.data.get('transaction_pin')

    # Validate required fields
    if not all([account_number, add_amount, transaction_pin]):
        return Response(
            {'message': "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate withdrawal amount type
    try:
        add_amount = Decimal(add_amount)
        if add_amount <= 0:
            raise ValueError
    except (TypeError, ValueError, InvalidOperation):
        return Response(
            {'message': "Invalid withdrawal amount."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch account
    account = BankAccount.objects.filter(account_number=account_number).first()
    if not account:
        return Response(
            {'message': "Account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Validate PIN
    if not check_password(transaction_pin, account.transaction_pin):
        return Response(
            {'message': "Incorrect PIN."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check balance
    # if add_amount > account.initial_deposit:  # Use `balance`, not `initial_deposit`
    #     return Response(
    #         {'message': "Insufficient funds."},
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    # Update balance
    account.initial_deposit += add_amount
    account.save()
    transaction_id = str(random.randint(10**9, 10**10 - 1))  # 10-digit ID
    reference_number = str(random.randint(10**7, 10**8 - 1))
    Transaction_Model.objects.create(
        account=account,
        transaction_type="deposit",
        amount=add_amount,
        transaction_id=transaction_id,
        reference_number=reference_number,
        status='completed',
        post_balance=account.initial_deposit
    )

    return Response(
        {
            'message': "Amount withdrawn successfully.",
            'current_balance': account.initial_deposit
        },
        status=status.HTTP_200_OK
    )