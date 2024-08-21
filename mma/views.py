from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FloatRequest, CustomUser, CashRequest, Balance, Transaction
from .forms import FloatRequestForm, CashRequestForm, BalanceUpdateForm
from django.db.models import Sum
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from .forms import ReportForm
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

@login_required
def download_receipt(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    html_string = render_to_string('mma/receipt.html', {'transaction': transaction})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{transaction_id}.pdf'
    return response

@login_required
def download_invoice(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    html_string = render_to_string('mma/invoice.html', {'transaction': transaction})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{transaction_id}.pdf'
    return response

def is_admin(user):
    return user.is_staff

def index(request):
    return render(request, 'mma/index.html')

@login_required
def receipt(request, transaction_id):
    # Retrieve the transaction object or return a 404 error if not found
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # Pass the transaction object to the context dictionary
    context = {
        'transaction': transaction,
    }
    # Render the 'receipt.html' template with the context data
    return render(request, 'mma/receipt.html', context)

@login_required
def invoice(request, transaction_id):
    # Retrieve the transaction object or return a 404 error if not found
    transaction = get_object_or_404(Transaction, id=transaction_id)
    # Pass the transaction object to the context dictionary
    context = {
        'transaction': transaction,
    }
    # Render the 'invoice.html' template with the context data
    return render(request, 'mma/invoice.html', context)

@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        'total_users': CustomUser.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'pending_float_requests': FloatRequest.objects.filter(is_approved=False).count(),
        'pending_cash_requests': CashRequest.objects.filter(is_approved=False).count(),
    }
    return render(request, 'mma/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'mma/admin_user_list.html', {'users': users})

@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'mma/admin_user_detail.html', {'user': user})

@user_passes_test(is_admin)
def admin_transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'mma/admin_transaction_list.html', {'transactions': transactions})

@user_passes_test(is_admin)
def admin_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Logic to generate reports based on form data
            report_data = form.cleaned_data  # Placeholder
            return render(request, 'mma/admin_report.html', {'report_data': report_data})
    else:
        form = ReportForm()
    return render(request, 'mma/admin_report.html', {'form': form})

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()  # Assuming a related name 'notifications'
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(request.user.notifications, id=notification_id)
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

@login_required
def dashboard(request):
    context = {
        'balance': Balance.objects.get(agent=request.user),
        'float_requests': FloatRequest.objects.filter(agent=request.user).order_by('-created_at')[:5],
        'cash_requests': CashRequest.objects.filter(agent=request.user).order_by('-created_at')[:5],
        'recent_transactions': Transaction.objects.filter(agent=request.user).order_by('-created_at')[:10],
    }
    return render(request, 'mma/dashboard.html', context)

@login_required
def enhanced_dashboard(request):
    agent = request.user
    balance = Balance.objects.get(agent=agent)

    # Get today's transactions
    today = timezone.now().date()
    today_transactions = Transaction.objects.filter(agent=agent, created_at__date=today)

    # Get this week's transactions
    week_start = today - timedelta(days=today.weekday())
    week_transactions = Transaction.objects.filter(agent=agent, created_at__date__gte=week_start)

    # Calculate some metrics
    total_transactions = today_transactions.count()
    total_volume = today_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'balance': balance,
        'total_transactions': total_transactions,
        'total_volume': total_volume,
        'recent_transactions': today_transactions.order_by('-created_at')[:5],
        'week_stats': {
            'transaction_count': week_transactions.count(),
            'transaction_volume': week_transactions.aggregate(Sum('amount'))['amount__sum'] or 0,
        },
        'float_requests': FloatRequest.objects.filter(agent=agent, is_approved=False),
        'cash_requests': CashRequest.objects.filter(agent=agent, is_approved=False),
    }

    return render(request, 'mma/enhanced_dashboard.html', context)

@login_required
def request_float(request):
    if request.method == 'POST':
        form = FloatRequestForm(request.POST)
        if form.is_valid():
            float_request = form.save(commit=False)
            float_request.agent = request.user
            float_request.save()
            return redirect('dashboard')
    else:
        form = FloatRequestForm()
    return render(request, 'mma/request_float.html', {'form': form})

@login_required
def request_cash(request):
    if request.method == 'POST':
        form = CashRequestForm(request.POST)
        if form.is_valid():
            cash_request = form.save(commit=False)
            cash_request.agent = request.user
            cash_request.save()
            return redirect('dashboard')
    else:
        form = CashRequestForm()
    return render(request, 'mma/request_cash.html', {'form': form})

@login_required
def update_balance(request):
    if request.method == 'POST':
        form = BalanceUpdateForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction_type = form.cleaned_data['transaction_type']
            service = form.cleaned_data.get('service')

            balance, created = Balance.objects.get_or_create(agent=request.user)

            if transaction_type == 'cash':
                balance.cash += amount
            else:
                balance.float += amount

            balance.save()

            Transaction.objects.create(
                agent=request.user,
                amount=amount,
                transaction_type=f'{transaction_type}_update',
            )

            return redirect('dashboard')
    else:
        form = BalanceUpdateForm()
    return render(request, 'mma/update_balance.html', {'form': form})

@staff_member_required
def admin_approval(request):
    pending_users = CustomUser.objects.filter(is_approved=False)
    pending_float_requests = FloatRequest.objects.filter(is_approved=False)
    pending_cash_requests = CashRequest.objects.filter(is_approved=False)

    context = {
        'pending_users': pending_users,
        'pending_float_requests': pending_float_requests,
        'pending_cash_requests': pending_cash_requests,
    }
    return render(request, 'mma/admin_approval.html', context)

@staff_member_required
def approve_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_approved = True
    user.save()
    return redirect('admin_approval')

@staff_member_required
def approve_float_request(request, request_id):
    float_request = FloatRequest.objects.get(id=request_id)
    float_request.is_approved = True
    float_request.save()

    balance, created = Balance.objects.get_or_create(agent=float_request.agent)
    balance.float += float_request.amount
    balance.save()

    Transaction.objects.create(
        agent=float_request.agent,
        amount=float_request.amount,
        transaction_type='float_approved'
    )

    return redirect('admin_approval')

@staff_member_required
def approve_cash_request(request, request_id):
    cash_request = CashRequest.objects.get(id=request_id)
    cash_request.is_approved = True
    cash_request.save()

    balance, created = Balance.objects.get_or_create(agent=cash_request.agent)
    balance.cash += cash_request.amount
    balance.save()

    Transaction.objects.create(
        agent=cash_request.agent,
        amount=cash_request.amount,
        transaction_type='cash_approved'
    )

    return redirect('admin_approval')

def calculate_interest():
    yesterday = timezone.now().date() - timedelta(days=1)
    balances = Balance.objects.all()

    for balance in balances:
        agent_amount = balance.cash + balance.float
        requested_amount = FloatRequest.objects.filter(agent=balance.agent, is_approved=True, created_at__date=yesterday).aggregate(Sum('amount'))['amount__sum'] or 0
        requested_amount += CashRequest.objects.filter(agent=balance.agent, is_approved=True, created_at__date=yesterday).aggregate(Sum('amount'))['amount__sum'] or 0

        agent_interest = agent_amount * Decimal('0.03')
        requested_interest = requested_amount * Decimal('0.15')
        total_interest = agent_interest + requested_interest

        balance.interest += total_interest
        balance.save()

        Transaction.objects.create(
            agent=balance.agent,
            amount=total_interest,
            transaction_type='interest_added'
        )

    print(f"Interest calculated for {timezone.now().date()}")


@login_required
def cashout(request):
    balance = Balance.objects.get(agent=request.user)
    total_amount = balance.cash + balance.float + balance.interest

    if request.method == 'POST':
        Transaction.objects.create(
            agent=request.user,
            amount=total_amount,
            transaction_type='cashout'
        )
        balance.cash = 0
        balance.float = 0
        balance.interest = 0
        balance.save()
        return redirect('dashboard')

    context = {
        'balance': balance,
        'total_amount': total_amount,
    }
    return render(request, 'mma/cashout.html', context)

def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'mma/transaction_list.html', {'transactions': transactions})

def transaction_detail(request, id):
    transaction = get_object_or_404(Transaction, id=id)
    return render(request, 'mma/transaction_detail.html', {'transaction': transaction})

def float_request_list(request):
    float_requests = FloatRequest.objects.all()
    return render(request, 'mma/float_request_list.html', {'float_requests': float_requests})

def cash_request_list(request):
    cash_requests = CashRequest.objects.all()
    return render(request, 'mma/cash_request_list.html', {'cash_requests': cash_requests})

def float_request_detail(request, id):
    float_request = get_object_or_404(FloatRequest, id=id)
    return render(request, 'mma/float_request_detail.html', {'float_request': float_request})

