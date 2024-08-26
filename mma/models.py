from django.db import models
from users.models import CustomUser
from django.db import models
from django.utils import timezone
from decimal import Decimal

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
    expiration_date = models.DateTimeField(null=True, blank=True)

    def days_until_expiration(self):
        if self.expiration_date:
            now = timezone.now()
            time_left = self.expiration_date - now
            return max(0, time_left.days)
        return None

class CashoutRequest(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Cashout Request {self.id} by {self.agent.username}"

class Balance(models.Model):
    agent = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    request_limit = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_cashout = models.DateField(null=True, blank=True)
    float = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_request_limit(self):
        self.request_limit = self.request_limit * Decimal('1.5')
        self.save()

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