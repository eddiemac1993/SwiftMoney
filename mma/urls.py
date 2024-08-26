from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('enhanced-dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),  # Added enhanced dashboard

    path('request-float/', views.request_float, name='request_float'),
    path('request-cash/', views.request_cash, name='request_cash'),
    path('update-balance/', views.update_balance, name='update_balance'),

    path('admin-approval/', views.admin_approval, name='admin_approval'),
    path('admin-approve-cashout/', views.approve_cashout, name='approve_cashout'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('approve-float-request/<int:request_id>/', views.approve_float_request, name='approve_float_request'),
    path('approve-cash-request/<int:request_id>/', views.approve_cash_request, name='approve_cash_request'),

    path('transactions/', views.transaction_list, name='transaction_list'),  # Added transaction list view
    path('transactions/<int:id>/', views.transaction_detail, name='transaction_detail'),  # Added transaction detail view

    path('float-requests/', views.float_request_list, name='float_request_list'),  # Added float request list view
    path('cash-requests/', views.cash_request_list, name='cash_request_list'),  # Added cash request list view
    path('float-requests/<int:id>/', views.float_request_detail, name='float_request_detail'),

    path('cashout/', views.cashout, name='cashout'),
        # Receipt and Invoice URLs
    path('receipt/<int:transaction_id>/', views.receipt, name='receipt'),
    path('invoice/<int:transaction_id>/', views.invoice, name='invoice'),

    path('receipt/<int:transaction_id>/download/', views.download_receipt, name='download_receipt'),
    path('invoice/<int:transaction_id>/download/', views.download_invoice, name='download_invoice'),

    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('adashboard/', views.admin_dashboard, name='a_dashboard'),
    path('a/users/', views.admin_user_list, name='a_user_list'),
    path('a/users/<int:user_id>/', views.admin_user_detail, name='a_user_detail'),
    path('a/transactions/', views.admin_transaction_list, name='a_transaction_list'),
    path('a/report/', views.admin_report, name='a_report'),

    path('a/approval/', views.admin_approval, name='a_approval'),
    path('a/approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('a/approve_float_request/<int:request_id>/', views.approve_float_request, name='approve_float_request'),
    path('a/approve_cash_request/<int:request_id>/', views.approve_cash_request, name='approve_cash_request'),

    # Error Pages (handled automatically by Django, add custom templates in your templates folder)
    # path('404/', views.custom_404_view, name='custom_404'),  # Custom 404 view (optional)
    # path('500/', views.custom_500_view, name='custom_500'),  # Custom 500 view (optional)
    # path('403/', views.custom_403_view, name='custom_403'),  # Custom 403 view (optional)
]
