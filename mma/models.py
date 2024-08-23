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

from django.db import models
from django.utils import timezone
from decimal import Decimal

class Balance(models.Model):
    agent = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_cashout = models.DateField(null=True, blank=True)
    float = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_balance(self, transaction):
        if transaction.transaction_type == 'float_request':
            self.float += transaction.amount
        elif transaction.transaction_type == 'cash_request':
            self.cash += transaction.amount
        elif transaction.transaction_type == 'cashout':
            self.cash -= transaction.amount
            self.float -= transaction.amount
            self.interest = 0
        self.save()

    def calculate_interest(self):
        days_since_last_cashout = (timezone.now().date() - self.last_cashout).days if self.last_cashout else 0
        self.interest += (self.cash + self.float) * Decimal('0.01') * days_since_last_cashout
        self.save()

class Transaction(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # e.g., 'float_request', 'cash_request', 'cashout'
    created_at = models.DateTimeField(auto_now_add=True)