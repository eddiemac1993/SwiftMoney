from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('enhanced-dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),  # Added enhanced dashboard

    path('request-float/', views.request_float, name='request_float'),
    path('request-cash/', views.request_cash, name='request_cash'),
    path('update-balance/', views.update_balance, name='update_balance'),

    path('admin-approval/', views.admin_approval, name='admin_approval'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('approve-float-request/<int:request_id>/', views.approve_float_request, name='approve_float_request'),
    path('approve-cash-request/<int:request_id>/', views.approve_cash_request, name='approve_cash_request'),

    path('transactions/', views.transaction_list, name='transaction_list'),  # Added transaction list view
    path('transactions/<int:id>/', views.transaction_detail, name='transaction_detail'),  # Added transaction detail view

    path('float-requests/', views.float_request_list, name='float_request_list'),  # Added float request list view
    path('cash-requests/', views.cash_request_list, name='cash_request_list'),  # Added cash request list view

    path('cashout/', views.cashout, name='cashout'),
        # Receipt and Invoice URLs
    path('receipt/<int:transaction_id>/', views.receipt, name='receipt'),
    path('invoice/<int:transaction_id>/', views.invoice, name='invoice'),

    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/transactions/', views.admin_transaction_list, name='admin_transaction_list'),
    path('admin/report/', views.admin_report, name='admin_report'),

    # Notifications URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),

    # Error Pages (handled automatically by Django, add custom templates in your templates folder)
    # path('404/', views.custom_404_view, name='custom_404'),  # Custom 404 view (optional)
    # path('500/', views.custom_500_view, name='custom_500'),  # Custom 500 view (optional)
    # path('403/', views.custom_403_view, name='custom_403'),  # Custom 403 view (optional)
]
