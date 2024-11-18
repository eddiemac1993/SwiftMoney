from django.db import models
from users.models import CustomUser
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import random
import string

# Generate a random 6-character code for each user
def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    username = models.CharField(max_length=255, default=generate_random_name)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.text[:20]}"


class QuizQuestion(models.Model):
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        return self.question_text

class QuizScore(models.Model):
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    score = models.IntegerField(default=0)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.score} points"

class Synonym(models.Model):
    term = models.CharField(max_length=255, unique=True)
    main_term = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.term} -> {self.main_term}"

class SearchLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    search_term = models.CharField(max_length=255)
    search_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user} searched for {self.search_term} on {self.search_date}"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('groceries', 'Groceries'),
        ('service', 'Service'),
        ('job', 'Job'),
        ('hardware', 'Hardware'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('automotive', 'Automotive'),
        ('beauty_health', 'Beauty & Health'),
        ('toys', 'Toys'),
        ('sports', 'Sports & Outdoors'),
        ('books', 'Books'),
        ('home_appliances', 'Home Appliances'),
        ('stationery', 'Stationery'),
        ('pharmacy', 'Pharmacy'),
        ('jewelry', 'Jewelry & Accessories'),
        ('footwear', 'Footwear'),
        ('gardening', 'Gardening & Outdoor'),
        ('baby_products', 'Baby Products'),
        ('pet_supplies', 'Pet Supplies'),
        ('music_instruments', 'Musical Instruments'),
        ('office_supplies', 'Office Supplies'),
        ('gaming', 'Gaming'),
        ('kitchenware', 'Kitchenware'),
        ('building_materials', 'Building Materials'),
        ('tools', 'Tools & Equipment'),
        ('computer_accessories', 'Computer & Accessories'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True, default='product_default.png')
    verified = models.BooleanField(default=False)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    # Add stock field
    stock_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    store_address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, default="000-000-0000", help_text="Enter the store owner's contact number")


    def get_google_maps_link(self):
        if self.store_address:
            # Use store_address to generate a Google Maps link
            return f"https://www.google.com/maps/search/?api=1&query={self.store_address.replace(' ', '+')}"
        return None

    def save(self, *args, **kwargs):
        if self.added_by and self.added_by.is_authenticated:
            self.verified = True
        else:
            self.verified = False
        super().save(*args, **kwargs)

    def update_stock(self, quantity, operation='decrease'):
        """
        Update product stock count
        operation: 'decrease' for sales, 'increase' for restocking
        """
        if operation == 'decrease':
            if self.stock_count >= quantity:
                self.stock_count -= quantity
            else:
                raise ValidationError(f"Insufficient stock for {self.name}. Available: {self.stock_count}")
        else:
            self.stock_count += quantity
        self.save()

    def __str__(self):
        return f"{self.name} (Stock: {self.stock_count})"


class Cart(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} sold"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),  # Add 'completed' status
        ('cancelled', 'Cancelled'),
    )

    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Allow null values
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    business_location = models.CharField(max_length=200, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)


    def complete_order(self):
        try:
            # Check stock availability for all items
            for item in self.items.all():
                if item.product.stock_count < item.quantity:
                    raise ValidationError(
                        f"Insufficient stock for {item.product.name}. "
                        f"Required: {item.quantity}, Available: {item.product.stock_count}"
                    )

            # Update stock counts and create sales records
            for item in self.items.all():
                item.product.update_stock(item.quantity, 'decrease')
                Sale.objects.create(
                    product=item.product,
                    user=self.agent,
                    quantity=item.quantity,
                    total_price=item.subtotal(),
                )

            self.status = 'completed'
            self.save()

        except ValidationError as e:
            raise ValidationError(f"Cannot complete order: {str(e)}")

    def calculate_delivery_date(self):
        if self.pk and self.items.exists():
            additional_delay = 2
            longest_delivery_time = max(
                item.product.delivery_time + additional_delay for item in self.items.all()
            )
            return timezone.now().date() + timezone.timedelta(days=longest_delivery_time)
        return timezone.now().date()

    def save(self, *args, **kwargs):
        if not self.delivery_date:
            self.delivery_date = self.calculate_delivery_date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"


@receiver(post_save, sender=Order)
def handle_order_status(sender, instance, **kwargs):
    # If the order status changes to cancelled, restore the stock
    if instance.status == 'cancelled':
        for item in instance.items.all():
            item.product.update_stock(item.quantity, 'increase')

@receiver(post_save, sender=Order)
def update_order_delivery_date(sender, instance, **kwargs):
    if kwargs.get('created', False):  # Only update on creation
        instance.delivery_date = instance.calculate_delivery_date()
        instance.save(update_fields=['delivery_date'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    issued_at = models.DateTimeField(auto_now_add=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_amount_due(self):
        return self.order.total_amount * Decimal('0.3')  # 30% deposit

    def save(self, *args, **kwargs):
        self.amount_due = self.calculate_amount_due()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice for Order {self.order.id}"

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

    def calculate_refund(self):
        return self.order.deposit_amount * Decimal('0.15')

    def save(self, *args, **kwargs):
        self.amount = self.calculate_refund()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Refund for Order {self.order.id}"


@receiver(post_save, sender=get_user_model())
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(agent=instance)

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
    request_limit = models.DecimalField(max_digits=10, decimal_places=2, default=100)
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