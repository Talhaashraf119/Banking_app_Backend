from django.db import models
# Create your models here.
import uuid
class Transaction_Model(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    Status_Choices=[
        ('pending','Pending'),
        ('complete','Complete'),
        ('failed','Failed'),
    ]
    account=models.ForeignKey('bankingapp.BankAccount',on_delete=models.CASCADE,related_name='transaction')
    transaction_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status_Choices, default='pending')
    post_balance = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.account.account_number} - {self.transaction_type} - {self.amount}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['account', 'timestamp']),
            models.Index(fields=['transaction_type']),
        ]
