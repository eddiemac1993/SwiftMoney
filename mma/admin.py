from django.contrib import admin
from .models import FloatRequest, CashRequest, Balance, Transaction

@admin.register(FloatRequest)
class FloatRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'service', 'is_approved', 'created_at')
    list_filter = ('service', 'is_approved', 'created_at')
    search_fields = ('agent__username', 'service', 'amount')
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(is_approved=True)
    approve_requests.short_description = "Approve selected Float Requests"


@admin.register(CashRequest)
class CashRequestAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('agent__username', 'amount')
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(is_approved=True)
    approve_requests.short_description = "Approve selected Cash Requests"


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('agent', 'cash', 'float', 'interest')
    search_fields = ('agent__username', 'cash', 'float', 'interest')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('agent__username', 'transaction_type', 'amount')

