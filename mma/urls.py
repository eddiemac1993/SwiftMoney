from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name='home'),
    path('create-wish/', views.create_wish, name='create_wish'),
    path('view-wish/<int:wish_id>/', views.view_wish, name='view_wish'),
    path('games/', views.games_hub, name='games_hub'),
    path('chat/', views.chat_home, name='chat_home'),
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('join/<str:room_name>/', views.join_room, name='join_room'),
    path('create-room/', views.create_room, name='create_room'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('submit-score/', views.submit_score_view, name='submit_score'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/pdf/', views.generate_sales_pdf, name='generate_sales_pdf'),
    path('download-report/', views.download_report, name='download_report'),
    path('completed-orders/', views.completed_orders, name='completed_orders'),
    path('complete_order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('search-logs/', views.search_log_view, name='search_logs'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/like/', views.like_dislike_product, {'action': 1}, name='like_product'),
    path('product/<int:product_id>/dislike/', views.like_dislike_product, {'action': -1}, name='dislike_product'),
    path('adminz/product-likes/', views.admin_product_likes, name='admin_product_likes'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('partnerships/', views.partnerships, name='partnerships'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('request-float/', views.request_float, name='request_float'),
    path('request-cash/', views.request_cash, name='request_cash'),
    path('update-balance/', views.update_balance, name='update_balance'),

    path('admin-approval/', views.admin_approval, name='admin_approval'),
    path('admin-approve-cashout/', views.approve_cashout, name='approve_cashout'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('approve-float-request/<int:request_id>/', views.approve_float_request, name='approve_float_request'),
    path('approve-cash-request/<int:request_id>/', views.approve_cash_request, name='approve_cash_request'),
    path('approve-orders/', views.admin_approve_orders, name='admin_approve_orders'),

    path('terms-and-conditions/', views.terms_and_conditions, name='terms-and-conditions'),

    path('approved-orders/', views.approved_order_list, name='approved_order_list'),
    path('generate/<int:order_id>/<str:doc_type>/', views.generate_document, name='generate_document'),

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
    path('refund/<int:order_id>/create/', views.refund_create, name='refund_create'),
    path('refund/<int:order_id>/list/', views.refund_list, name='refund_list'),

    path('orders/<int:order_id>/refunds/', views.RefundListView.as_view(), name='order_refund_list'),
    path('refunds/<int:order_id>/', views.refund_detail, name='refund_detail'),

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

    path('', views.product_list, name='product_list'),
    path('agents/', views.agent_list, name='agent_list'),
    path('product-list/', views.product_list_anonymous, name='product_list_anonymous'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/pay-deposit/', views.pay_deposit, name='pay_deposit'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/summary/', views.order_summary, name='order_summary'),


    # Error Pages (handled automatically by Django, add custom templates in your templates folder)
    # path('404/', views.custom_404_view, name='custom_404'),  # Custom 404 view (optional)
    # path('500/', views.custom_500_view, name='custom_500'),  # Custom 500 view (optional)
    # path('403/', views.custom_403_view, name='custom_403'),  # Custom 403 view (optional)
]
