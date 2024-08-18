from django.db import models
from users.models import CustomUser

class FloatRequest(models.Model):
    SERVICES = [
        ('airtel', 'Airtel'),
        ('mtn', 'MTN'),
        ('zamtel', 'Zamtel'),
        ('zanaco', 'Zanaco'),
        ('fnb', 'FNB'),
    ]
    
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service = models.CharField(max_length=10, choices=SERVICES)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CashRequest(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Balance(models.Model):
    agent = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    float = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # e.g., 'float_request', 'cash_request', 'cashout'
    created_at = models.DateTimeField(auto_now_add=True)