from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, Invoice, Refund, FloatRequest, CashRequest, CashoutRequest, Balance, Transaction

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'delivery_time')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    ordering = ('name',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('agent', 'created_at', 'total_amount')
    search_fields = ('agent__username',)
    readonly_fields = ('total_amount',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal')
    search_fields = ('cart__agent__username', 'product__name')
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('agent', 'customer_name', 'total_amount', 'deposit_amount', 'status', 'created_at', 'delivery_date')
    search_fields = ('agent__username', 'customer_name')
    list_filter = ('status',)
    readonly_fields = ('delivery_date',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'subtotal')
    search_fields = ('order__agent__username', 'product__name')
    readonly_fields = ('subtotal',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'issued_at', 'amount_due')
    search_fields = ('order__agent__username',)
    readonly_fields = ('amount_due',)

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'issued_at')
    search_fields = ('order__agent__username',)
    readonly_fields = ('amount',)

@admin.register(FloatRequest)
class FloatRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'service', 'is_approved', 'created_at')
    search_fields = ('agent__username', 'service')
    list_filter = ('is_approved',)

@admin.register(CashRequest)
class CashRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'is_approved', 'created_at', 'expiration_date', 'days_until_expiration')
    search_fields = ('agent__username',)
    list_filter = ('is_approved',)
    readonly_fields = ('days_until_expiration',)

@admin.register(CashoutRequest)
class CashoutRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'is_approved', 'status', 'created_at', 'approved_at')
    search_fields = ('agent__username',)
    list_filter = ('status', 'is_approved')

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('agent', 'request_limit', 'cash', 'float', 'interest', 'last_cashout')
    search_fields = ('agent__username',)
    readonly_fields = ('request_limit', 'cash', 'float', 'interest', 'last_cashout')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'transaction_type', 'created_at')
    search_fields = ('agent__username', 'transaction_type')
    list_filter = ('transaction_type',)

