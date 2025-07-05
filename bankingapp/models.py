from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, RegexValidator

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('business', 'Business Account'),
        ('fixed', 'Fixed Deposit'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to Django's User model
    account_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(r'^\d{12}$', "Account number must be 12 digits.")]
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='savings')
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\+?\d{10,15}$', "Enter a valid phone number.")]
    )
    email = models.EmailField(unique=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(5)])
    occupation = models.CharField(max_length=100, blank=True, null=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    initial_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='uploads/images/',default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    # Security Fields
    transaction_pin = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{6}$', "PIN must be 6 digits.")])
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"