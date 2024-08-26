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
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CashoutRequest
from django.core.mail import send_mail
from django.conf import settings

@staff_member_required
def approve_cashout(request):
    if request.method == 'POST':
        cashout_id = request.POST.get('cashout_id')
        action = request.POST.get('action')

        cashout_request = get_object_or_404(CashoutRequest, id=cashout_id)

        if action == 'approve':
            cashout_request.is_approved = True
            cashout_request.approved_at = timezone.now()
            cashout_request.save()

            # Update agent's balance
            balance = Balance.objects.get(agent=cashout_request.agent)

            # Create a transaction for the approved cashout
            Transaction.objects.create(
                agent=cashout_request.agent,
                amount=cashout_request.amount,
                transaction_type='cashout'
            )

            # Update the balance
            balance.cash = 0
            balance.float = 0
            balance.last_cashout = timezone.now().date()
            balance.update_request_limit()  # Update the request limit
            balance.save()

            messages.success(request, f"Cashout request {cashout_id} approved successfully.")

        elif action == 'reject':
            cashout_request.delete()
            messages.success(request, f"Cashout request {cashout_id} rejected and deleted.")

        return redirect('approve_cashout')

    pending_requests = CashoutRequest.objects.filter(is_approved=False).order_by('created_at')
    return render(request, 'mma/approve_cashout.html', {'pending_requests': pending_requests})

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to the homepage or any other page

@receiver(post_save, sender=CustomUser)
def create_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(agent=instance)

from decimal import Decimal
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Balance, CashoutRequest

@login_required
def cashout(request):
    # Fetch or create the user's balance
    balance, created = Balance.objects.get_or_create(agent=request.user)

    # Check if the user already has a pending cashout request
    has_pending_request = CashoutRequest.objects.filter(agent=request.user, status='pending').exists()

    # Calculate the total amount (cash + float)
    requested_cash = balance.cash
    requested_float = balance.float
    total_requested = requested_cash + requested_float

    # Calculate 20% interest on the total requested amount
    interest = total_requested * Decimal('0.2') if total_requested > 0 else Decimal('0')

    # Calculate the total cashout amount (requested + interest)
    total_amount = total_requested + interest

    if request.method == 'POST':
        # Only proceed if the user has sufficient balance
        if total_requested > 0:
            if not has_pending_request:
                # Create a new cashout request
                CashoutRequest.objects.create(
                    agent=request.user,
                    amount=total_amount,
                    status='pending'
                )

                # Send notification email to admin
                send_mail(
                    'Cashout Request Submitted',
                    f"User {request.user.username} has requested a cashout of {total_amount} (including 20% interest).",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )

                messages.success(request, f"Cashout request for {total_amount} has been submitted for approval.")
                return redirect('dashboard')
            else:
                messages.error(request, "You already have a pending cashout request. Please wait for it to be processed.")
        else:
            messages.error(request, "You have no available balance to cash out.")

    context = {
        'balance': balance,
        'total_amount': total_amount,
        'interest': interest,
        'has_pending_request': has_pending_request,
    }
    return render(request, 'mma/cashout.html', context)


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
        'pending_cashout_requests': CashoutRequest.objects.filter(is_approved=False).count(),  # Added this line
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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Balance, CashoutRequest, CashRequest, Transaction

@login_required
def dashboard(request):
    agent = request.user
    balance, created = Balance.objects.get_or_create(agent=agent)

    # Get the latest cashout
    latest_cashout = CashoutRequest.objects.filter(agent=agent, is_approved=True).order_by('-created_at').first()

    # Get the current cash request (latest unapproved one)
    current_cash_request = CashRequest.objects.filter(agent=agent, is_approved=False).order_by('-created_at').first()

    # Calculate days until expiration
    days_until_expiration = None
    if current_cash_request and current_cash_request.expiration_date:
        now = timezone.now()
        time_left = current_cash_request.expiration_date - now
        days_until_expiration = max(0, time_left.days)

    # Calculate interest on cash
    cash_interest = calculate_interest(balance.cash)  # Ensure this function is defined or imported

    # Calculate total amount (cash + cash interest)
    total_amount = balance.cash + cash_interest

    # Get today's transactions
    today = timezone.now().date()
    today_transactions = Transaction.objects.filter(agent=agent, created_at__date=today)

    # Calculate some metrics
    total_transactions = today_transactions.count()
    total_volume = today_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'balance': balance,
        'latest_cashout': latest_cashout,
        'current_cash_request': current_cash_request,
        'days_until_expiration': days_until_expiration,
        'total_transactions': total_transactions,
        'total_volume': total_volume,
        'cash_requests': CashRequest.objects.filter(agent=agent).order_by('-created_at')[:5],
        'recent_transactions': Transaction.objects.filter(agent=agent).order_by('-created_at')[:10],
        'cash_interest': cash_interest,
        'total_amount': total_amount,
    }
    return render(request, 'mma/dashboard.html', context)

@login_required
def request_float(request):
    balance, created = Balance.objects.get_or_create(agent=request.user)

    if request.method == 'POST':
        form = FloatRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            # Check if the amount is within the allowed range
            if Decimal('1') <= amount <= balance.request_limit:
                float_request = form.save(commit=False)
                float_request.agent = request.user
                float_request.save()

                messages.success(request, f"Float request for {amount} has been submitted.")
                return redirect('dashboard')
            else:
                messages.error(request, f"Amount must be between 1 and {balance.request_limit}.")
    else:
        form = FloatRequestForm()

    # Calculate remaining limit for cash requests
    total_float_requests = FloatRequest.objects.filter(agent=request.user, is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_limit = balance.request_limit - total_float_requests

    context = {
        'form': form,
        'request_limit': balance.request_limit,
        'remaining_limit': remaining_limit,
    }
    return render(request, 'mma/request_float.html', context)

@login_required
def request_cash(request):
    balance, created = Balance.objects.get_or_create(agent=request.user)

    if request.method == 'POST':
        form = CashRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            # Calculate remaining limit
            total_requests = FloatRequest.objects.filter(agent=request.user, is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
            total_requests += CashRequest.objects.filter(agent=request.user, is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
            remaining_limit = balance.request_limit - total_requests

            if Decimal('100') <= amount <= remaining_limit:
                cash_request = form.save(commit=False)
                cash_request.agent = request.user
                cash_request.save()

                # Send notification email to admin
                send_mail(
                    'New Cash Request',
                    f'User {request.user.username} has submitted a cash request for {amount}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )

                messages.success(request, f"Cash request for {amount} has been submitted.")
                return redirect('dashboard')
            else:
                messages.error(request, f"Amount must be between k100 and k{remaining_limit}.")
    else:
        form = CashRequestForm()

    # Calculate remaining limit for cash requests
    total_requests = FloatRequest.objects.filter(agent=request.user, is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
    total_requests += CashRequest.objects.filter(agent=request.user, is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_limit = balance.request_limit - total_requests

    context = {
        'form': form,
        'request_limit': balance.request_limit,
        'remaining_limit': remaining_limit,
    }
    return render(request, 'mma/request_cash.html', context)

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
    balance.calculate_interest()

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
    cash_request.expiration_date = timezone.now() + timedelta(days=30)
    cash_request.save()

    balance, created = Balance.objects.get_or_create(agent=cash_request.agent)
    balance.cash += cash_request.amount
    balance.calculate_interest()

    Transaction.objects.create(
        agent=cash_request.agent,
        amount=cash_request.amount,
        transaction_type='cash_approved'
    )

    return redirect('admin_approval')

def calculate_interest(total_requested):
    # Calculate 20% interest
    return total_requested * Decimal('0.20')

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

