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
from .models import CashoutRequest, Sale
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Cart,Balance, CashoutRequest, CashRequest, Transaction, CartItem, Order, Invoice, Refund, OrderItem
from django.db import transaction
from .forms import OrderForm
from django.db.models import Q
from django.views import View
from django.views.generic import ListView
from .forms import RefundForm  # Assuming you have a form for handling refunds
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
import random
from .models import QuizQuestion, QuizScore
from .forms import SubmitScoreForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom, Message
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import ChatRoom
import string
from django.shortcuts import render

def games_hub(request):
    # Add any context data if needed
    return render(request, 'games_hub.html')

def chat_home(request):
    if request.method == "POST":
        # Create a new room
        room_name = request.POST.get('room_name')
        if room_name:
            ChatRoom.objects.create(name=room_name)
            return redirect('chat_room', room_name=room_name)

    # Retrieve all existing rooms
    rooms = ChatRoom.objects.all()
    return render(request, 'chat.html', {'rooms': rooms})

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            room, created = ChatRoom.objects.get_or_create(name=room_name)
            return redirect('join_room', room_name=room.name)
    return render(request, 'create_room.html')

from uuid import uuid4

def join_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)

    if request.method == 'POST':
        username = request.POST.get('username') or f"user_{uuid4().hex[:8]}"
        user = ChatUser.objects.create(
            room=room,
            username=username,
            is_originator=False,
        )
        return redirect('chat_room', room_name=room.name, username=user.username)

    return render(request, 'join_room.html', {'room': room})

from django.shortcuts import render, get_object_or_404
from .models import ChatRoom, Message

from collections import defaultdict

def chat_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)

    # Check if the username exists in the session, else generate one
    if 'username' not in request.session:
        request.session['username'] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    username = request.session['username']

    if request.method == "POST":
        message_text = request.POST.get('message')
        # Save the message to the database with the session's username
        Message.objects.create(room=room, username=username, text=message_text)

    # Get all messages for the room, ordered by newest first
    messages = room.messages.all().order_by('-timestamp')

    # Assign unique colors to each username
    usernames = messages.values_list('username', flat=True).distinct()
    color_map = {username: f"hsl({index * 50 % 360}, 70%, 80%)" for index, username in enumerate(usernames)}

    return render(request, 'chat_room.html', {
        'room': room,
        'username': username,
        'messages': messages,
        'color_map': color_map,
    })





def quiz_view(request):
    question = random.choice(QuizQuestion.objects.all())  # Random question
    score = request.session.get('score', 0)
    top_scores = QuizScore.objects.all().order_by('-score')[:5]# Retrieve session score, default is 0

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')

        # Update score based on the answer
        if selected_answer == correct_answer:
            score += 0.5  # Add 10 points for correct answer
        else:
            score -= 0.3  # Subtract 5 points for incorrect answer

        request.session['score'] = score  # Save score in session

        # Check if the user clicked the "Submit Score" button
        if 'submit_score' in request.POST:
            return redirect('submit_score')  # Redirect to submit_score page

        return redirect('quiz')  # Continue quiz after answering the question

    return render(request, 'quiz.html', {'question': question, 'top_scores': top_scores, 'score': score})

def submit_score_view(request):
    score = request.session.get('score', 0)  # Retrieve session score
    if request.method == 'POST':
        form = SubmitScoreForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.score = score
            submission.save()
            request.session['score'] = 0  # Reset session score
            return redirect('quiz')  # Redirect to the quiz page
    else:
        form = SubmitScoreForm()
    return render(request, 'submit_score.html', {'form': form, 'score': score})

def search_log_view(request):
    # Retrieve all search logs, ordered by date (newest first)
    search_logs = SearchLog.objects.all().order_by('-search_date')

    context = {
        'search_logs': search_logs
    }
    return render(request, 'mma/search_logs.html', context)


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def refund_list(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.order = order
            refund.save()
            # Redirect or return a response
    else:
        form = RefundForm()

    return render(request, 'mma/refund_list.html', {'form': form, 'order': order})

class RefundListView(ListView):
    model = Refund
    template_name = 'refund_list.html'

class RefundDetailView(View):
    def get(self, request, refund_id):
        refund = get_object_or_404(Refund, id=refund_id)
        context = {
            'refund': refund
        }
        return render(request, 'refund_detail.html', context)

def refund_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.order = order
            refund.save()
            return redirect('refund_detail', order_id=order.id)  # Correct view name and argument
    else:
        form = RefundForm()

    return render(request, 'refund_form.html', {'form': form, 'order': order})

def refund_detail(request, order_id):
    # Example view for showing refund details
    order = get_object_or_404(Order, id=order_id)
    refunds = order.refunds.all()
    return render(request, 'refund_detail.html', {'order': order, 'refunds': refunds})


@staff_member_required
def approved_order_list(request):
    approved_orders = Order.objects.filter(status='approved').order_by('-created_at')
    context = {
        'approved_orders': approved_orders,
    }
    return render(request, 'mma/approved_order_list.html', context)

@staff_member_required
def generate_document(request, order_id, doc_type):
    order = get_object_or_404(Order, id=order_id)

    # Check if the document type is invoice and the order is not approved
    if doc_type == 'invoice' and order.status != 'approved':
        return HttpResponse("Invoice can only be generated for approved orders.", status=400)

    # Calculate the estimated delivery time in days for invoice or receipt
    if order.delivery_date and doc_type in ['invoice', 'receipt']:
        delivery_days = (order.delivery_date - timezone.now().date()).days
    else:
        delivery_days = 'N/A'  # If delivery date is not set

    # Prepare context data based on the document type
    context = {
        'order': order,
        'delivery_days': delivery_days,
        'document_type': doc_type,
        'is_invoice_or_receipt': doc_type in ["invoice", "receipt"],
        'is_invoice_or_quotation': doc_type in ["invoice", "quotation"]
    }


    # Render the appropriate template
    html_string = render_to_string('mma/invoice_template.html', context)

    # Generate PDF
    html = HTML(string=html_string)
    pdf_result = html.write_pdf()

    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename={doc_type}_{order.id}.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    # Write PDF to response
    response.write(pdf_result)

    return response

def agent_list(request):
    query = request.GET.get('q')

    # Filter agents by business location if a search query is provided
    if query:
        agents = CustomUser.objects.filter(business_location__icontains=query, is_admin=False)
    else:
        agents = CustomUser.objects.filter(is_admin=False)

    return render(request, 'agent_list.html', {
        'agents': agents,
        'query': query,
    })

def product_list_anonymous(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_filter = request.GET.get('category')

    # Filter products by search query if provided
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        ).order_by('-created')
    else:
        products = Product.objects.all().order_by('-created')

    # Filter products by category if a category is selected
    if category_filter:
        products = products.filter(category=category_filter)

    # Filter by price range if provided
    if min_price and min_price.lower() != 'none':
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass  # Handle the case where conversion fails

    if max_price and max_price.lower() != 'none':
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass  # Handle the case where conversion fails

    # Pagination
    paginator = Paginator(products, 100)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all distinct categories from products
    categories = Product.objects.values_list('category', flat=True).distinct()

    # If the user is not authenticated, don't access user-specific data
    if isinstance(request.user, AnonymousUser):
        cart_item_count = 0
    else:
        try:
            cart = Cart.objects.get(agent=request.user)
            cart_item_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_item_count = 0

    return render(request, 'product_list.html', {
        'products': products,
        'query': query,
        'page_obj': page_obj,
        'min_price': min_price,
        'max_price': max_price,
        'categories': categories,  # Pass categories to the template
        'cart_item_count': cart_item_count  # Add the count to context
    })

from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Product, SearchLog, Synonym


def product_list(request):
    query = request.GET.get('q', '').strip()  # Ensure query is always a string, even if empty
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_filter = request.GET.get('category')
    verified_filter = request.GET.get('verified')

    # Start with all products, ordering by creation date (latest first)
    products = Product.objects.all().order_by('-created')

    new_arrival_threshold = timezone.now() - timedelta(days=4)
    new_arrivals = products.filter(created__gte=new_arrival_threshold)

    # Check for synonyms if a query is provided
    if query:
        synonym_entry = Synonym.objects.filter(term__iexact=query).first()
        main_term = synonym_entry.main_term if synonym_entry else query

        # Filter products based on the main term
        products = products.filter(
            Q(name__icontains=main_term) | Q(category__icontains=main_term)
        )

    # Log the search query (whether the user is logged in or not)
    search_term = query if query else "N/A"  # Avoid logging 'None' as search term

    SearchLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        search_term=search_term,
        search_date=timezone.now()
    )

    # Filter by category if provided
    if category_filter:
        products = products.filter(category=category_filter)

    # Filter by price range if provided
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Filter by verified status if provided
    if verified_filter:
        products = products.filter(verified=True)

    # Pagination
    paginator = Paginator(products, 100)  # Show 100 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get distinct categories for filtering options
    categories = Product.objects.values_list('category', flat=True).distinct()

    # Handle cart item count for authenticated users
    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(agent=request.user)
            cart_item_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

    can_add_product = True  # Allow all users to add a product

    low_stock_threshold = 5

    context = {
        'products': products,  # Keep this for the total products (not paginated)
        'query': query,
        'new_arrivals': new_arrivals,
        'page_obj': page_obj,  # This is the paginated product list
        'min_price': min_price,
        'max_price': max_price,
        'categories': categories,
        'cart_item_count': cart_item_count,
        'low_stock_threshold': low_stock_threshold,
        'can_add_product': can_add_product,
        'verified_filter': verified_filter,
    }

    return render(request, 'product_list.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    # Get the product by ID or return 404 if not found
    product = get_object_or_404(Product, id=product_id)

    # Check if the user is authenticated to show cart item count
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(agent=request.user)
            cart_item_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_item_count = 0
    else:
        cart_item_count = 0  # If the user is not authenticated, cart count is 0

    return render(request, 'product_detail.html', {
        'product': product,
        'cart_item_count': cart_item_count  # Pass the cart item count
    })

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the logged-in user is the owner
    if request.user != product.added_by:
        return redirect('product_detail', product_id=product_id)  # Redirect if not owner

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_edit.html', {'form': form, 'product': product})


# views.py
from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm  # Assuming you have a ProductForm defined

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Check if the user is authenticated
            if request.user.is_authenticated:
                product.added_by = request.user  # Assign logged-in user
            else:
                product.added_by = None  # Or handle as needed
            product.save()
            return redirect('/')  # Redirect to a success page
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})



@login_required
def add_to_cart(request, product_id):
    # Get the product, or return 404 if not found
    product = get_object_or_404(Product, id=product_id)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(agent=request.user)

    # Get or create a cart item for the product
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    # If the cart item already exists, increment the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"Quantity updated: {product.name} is now {cart_item.quantity} in your cart.")
    else:
        messages.success(request, f"{product.name} added to your cart.")

    # Redirect back to the same page (or product list as fallback)
    next_url = request.GET.get('next', 'product_list')
    return redirect(next_url)

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(agent=request.user)
        cart_items = cart.items.all()
        total_amount = cart.total_amount()
        cart_item_count = cart_items.count()  # Calculate the number of items
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
        total_amount = 0
        cart_item_count = 0

    # Handle POST requests for updating quantity or removing items
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            if action == 'update_quantity':
                new_quantity = int(request.POST.get('quantity'))
                if new_quantity > 0:
                    item.quantity = new_quantity
                    item.save()
            elif action == 'remove_item':
                item.delete()
        except CartItem.DoesNotExist:
            pass

        return redirect('view_cart')  # Redirect to the cart page after action

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_item_count': cart_item_count,  # Add the count to context
    }
    return render(request, 'view_cart.html', context)


@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(agent=request.user)

        # Check if the cart has items
        if not cart.items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')

        # Handle the form submission
        if request.method == 'POST':
            form = OrderForm(request.POST)

            if form.is_valid():
                # Call the order submission function if the form is valid
                return submit_order(request, form.cleaned_data)
            else:
                # Form is invalid
                messages.error(request, "There was an error in your form. Please check your details.")
        else:
            # Display the order form if no POST request is made
            form = OrderForm()

        context = {
            'form': form,
            'cart': cart,
            'total': cart.total_amount(),  # Pass the total cart amount to the context
        }
        return render(request, 'checkout.html', context)

    # Handle case where cart does not exist for the user
    except Cart.DoesNotExist:
        messages.error(request, "You don't have an active cart.")
        return redirect('product_list')

@login_required
@transaction.atomic
@login_required
@transaction.atomic
def submit_order(request, form_data):
    try:
        cart = Cart.objects.get(agent=request.user)
        order = Order.objects.create(
            agent=request.user,
            customer_name=form_data['customer_name'],
            phone_number=form_data['phone_number'],
            total_amount=cart.total_amount(),
            deposit_amount=cart.total_amount() * Decimal('0.3'),
            status='pending'
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        Invoice.objects.create(order=order)
        cart.items.all().delete()
        messages.success(request, f"Order #{order.id} submitted successfully.")
        return redirect('order_confirmation', order_id=order.id)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('checkout')

@login_required
def complete_order(request, order_id):
    try:
        # Get the order by ID or raise a 404 if it doesn't exist
        order = get_object_or_404(Order, id=order_id, agent=request.user)

        # Update the order status to 'approved'
        order.status = 'approved'

        # Call a method to log sales or any additional processing
        order.complete_order()  # Ensure this method exists in your Order model

        # Save the updated order
        order.save()

        # Optionally, you can redirect to an order detail or confirmation page
        return redirect('order_detail', order_id=order.id)

    except Exception as e:
        messages.error(request, f"An error occurred while completing the order: {str(e)}")
        return redirect('order_detail', order_id=order_id)


@login_required
def completed_orders(request):
    user = request.user

    # Admins can see all completed orders
    if user.is_staff:
        completed_orders = Order.objects.filter(status='completed')
    else:
        # Allow agents to see all completed orders associated with their business location
        completed_orders = Order.objects.filter(status='completed')

        # Further filter by business location if the user has one
        if hasattr(user, 'business_location') and user.business_location:
            completed_orders = completed_orders.filter(business_location=user.business_location)

    # Get the current date and month
    today = timezone.now().date()
    current_month = timezone.now().month

    # Calculate daily sales
    daily_sales = completed_orders.filter(created_at__date=today).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Calculate monthly sales
    monthly_sales = completed_orders.filter(created_at__month=current_month).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    context = {
        'completed_orders': completed_orders,
        'daily_sales': float(daily_sales),
        'monthly_sales': float(monthly_sales),
    }

    return render(request, 'completed_orders.html', context)


def mark_order_as_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'approved':
        order.complete_order()
        messages.success(request, f"Order {order.id} has been marked as completed.")
    else:
        messages.error(request, "Only approved orders can be completed.")

    return redirect('order_detail', order_id=order.id)

from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import Order
import tempfile

def download_report(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to log in to download the report.", status=403)

    user = request.user
    completed_orders = Order.objects.filter(status='completed', agent=user)

    # Optionally filter by user's location
    if user.business_location:  # Ensure user has a location attribute
        completed_orders = completed_orders.filter(business_location=user.business_location)

    # Prepare the context with the completed orders
    context = {
        'completed_orders': completed_orders,
        'user': user,
    }

    # Render the HTML template to a string
    html_string = render_to_string('order_report_template.html', context)

    # Convert the HTML to PDF
    html = HTML(string=html_string)
    pdf_content = html.write_pdf()

    # Create the HTTP response with PDF content
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="completed_orders_report.pdf"'

    return response



@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, agent=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    invoice = order.invoice
    return render(request, 'order_detail.html', {'order': order, 'invoice': invoice})

@login_required
def pay_deposit(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Simulate the deposit payment process here
        # You can integrate with a payment gateway like Stripe, PayPal, etc.

        # If payment is successful:
        order.status = 'approved'
        order.save()

        messages.success(request, f"Deposit of {order.deposit_amount} has been paid successfully.")
        return redirect('order_detail', order_id=order.id)

    return render(request, 'pay_deposit.html', {'order': order})

@login_required
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()

        # Issue a refund for 15% of the deposit
        refund_amount = order.deposit_amount * Decimal('0.15')
        Refund.objects.create(order=order, amount=refund_amount)

        return redirect('order_detail', order_id=order.id)

    return redirect('order_detail', order_id=order.id)

def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    delivery_date = order.calculate_delivery_date()

    return render(request, 'order_summary.html', {'order': order, 'delivery_date': delivery_date})

@staff_member_required
def admin_approve_orders(request):
    pending_orders = Order.objects.filter(status='pending')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')

        order = get_object_or_404(Order, id=order_id)

        if action == 'approve':
            order.status = 'approved'
            order.approved_by = request.user
            order.save()
            messages.success(request, f"Order #{order.id} has been approved.")
        elif action == 'reject':
            order.status = 'cancelled'
            order.save()
            messages.warning(request, f"Order #{order.id} has been rejected.")

        return redirect('admin_approve_orders')

    return render(request, 'approve_orders.html', {'pending_orders': pending_orders})

@staff_member_required
def approve_cashout(request):
    if request.method == 'POST':
        cashout_id = request.POST.get('cashout_id')
        action = request.POST.get('action')

        cashout_request = get_object_or_404(CashoutRequest, id=cashout_id)

        if action == 'approve':
            cashout_request.status = 'approved'
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

            # Reset balance after cashout
            balance.cash = 0
            balance.float = 0
            balance.last_cashout = timezone.now().date()
            balance.update_request_limit()
            balance.save()

            messages.success(request, f"Cashout request {cashout_id} approved successfully.")

        elif action == 'reject':
            cashout_request.status = 'rejected'
            cashout_request.save()
            messages.success(request, f"Cashout request {cashout_id} rejected.")

        return redirect('approve_cashout')

    pending_requests = CashoutRequest.objects.filter(status='pending').order_by('created_at')
    return render(request, 'mma/approve_cashout.html', {'pending_requests': pending_requests})

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to the homepage or any other page

@receiver(post_save, sender=CustomUser)
def create_balance(sender, instance, **kwargs):
    # Check if a Balance already exists for the agent
    if not Balance.objects.filter(agent=instance).exists():
        Balance.objects.create(agent=instance)

@login_required
def cashout(request):
    balance, created = Balance.objects.get_or_create(agent=request.user)

    # Check if the user already has a pending cashout request
    has_pending_request = CashoutRequest.objects.filter(agent=request.user, status='pending').exists()

    requested_cash = balance.cash
    requested_float = balance.float
    total_requested = requested_cash + requested_float

    interest = total_requested * Decimal('0.2') if total_requested > 0 else Decimal('0')
    total_amount = total_requested + interest

    if request.method == 'POST':
        if total_requested > 0:
            if not has_pending_request:
                # Create a new cashout request
                CashoutRequest.objects.create(
                    agent=request.user,
                    amount=total_amount,
                    status='pending'
                )

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
        'pending_cashout_requests': CashoutRequest.objects.filter(status='Pending').count(),  # Adjust this line
    }
    return render(request, 'mma/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_user_list(request):
    users = CustomUser.objects.all()

    # Prepare a list of dictionaries containing user and balance data
    user_data = []
    for user in users:
        balance = Balance.objects.filter(agent=user).first()  # Fetch the balance for each user
        user_data.append({
            'user': user,
            'balance': balance.cash if balance else 0.00  # Assuming 'cash' is the balance field
        })

    return render(request, 'mma/admin_user_list.html', {'user_data': user_data})

@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'mma/admin_user_detail.html', {'user': user})

@user_passes_test(is_admin)
def admin_transaction_list(request):
    transactions = Transaction.objects.all()

    # Calculate total cash in (when agents cash out, i.e., money comes into the system)
    total_cash_in = transactions.filter(transaction_type='cashout').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Calculate total cash out (money given to agents upon their request)
    total_cash_out = transactions.filter(transaction_type__in=['float_request', 'cash_request']).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    return render(request, 'mma/admin_transaction_list.html', {
        'transactions': transactions,
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out
    })

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

            if Decimal('50') <= amount <= remaining_limit:
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
                messages.error(request, f"Amount must be between k50 and k{remaining_limit}.")
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
    pending_orders = Order.objects.filter(status='pending')

    context = {
        'pending_users': pending_users,
        'pending_float_requests': pending_float_requests,
        'pending_cash_requests': pending_cash_requests,
        'pending_orders': pending_orders,
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

def partnerships(request):
    # Your logic here
    return render(request, 'mma/partnerships.html')



# views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from django_filters import FilterSet, DateFromToRangeFilter, ChoiceFilter
import django_filters
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

class OrderFilter(FilterSet):
    created_at = DateFromToRangeFilter()
    status = ChoiceFilter(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['agent', 'status', 'created_at']

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related('agent').prefetch_related('items__product')
        self.filterset = OrderFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset

        # Calculate totals for filtered results
        filtered_orders = self.filterset.qs
        context['total_amount'] = filtered_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['total_deposits'] = filtered_orders.aggregate(Sum('deposit_amount'))['deposit_amount__sum'] or 0

        return context

# views.py
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from django.conf import settings
import tempfile
from datetime import datetime
from django.db.models import Sum
import os

def generate_sales_pdf(request):
    # Get filtered queryset
    queryset = OrderFilter(request.GET, queryset=Order.objects.all()).qs

    # Calculate summary data
    summary_data = {
        'total_amount': queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_deposits': queryset.aggregate(Sum('deposit_amount'))['deposit_amount__sum'] or 0,
        'total_orders': queryset.count(),
        'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'date_range': {
            'start': request.GET.get('created_at_after', 'All time'),
            'end': request.GET.get('created_at_before', 'Present')
        }
    }

    # Prepare orders data with product details
    orders_data = []
    for order in queryset:
        products = ", ".join([f"{item.quantity}x {item.product.name}" for item in order.items.all()])
        orders_data.append({
            'date': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'agent': order.agent.username,
            'customer': order.customer_name,
            'products': products,
            'total': order.total_amount,
            'deposit': order.deposit_amount,
            'status': order.status
        })

    # Render the HTML template
    html_string = render_to_string('pdf_template.html', {
        'orders': orders_data,
        'summary': summary_data,
        'company_name': 'SwiftStyles Co.',
        'company_address': 'Monze',
        'company_phone': '+260773351643',
        'company_email': 'swiftstyles@gmail.com'
    })

    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.now().strftime("%Y%m%d")}.pdf"'

    # Generate PDF
    HTML(string=html_string).write_pdf(
        response,
        stylesheets=[
            CSS(string='''
                @page {
                    size: letter portrait;
                    margin: 2.5cm;
                    @top-right {
                        content: "Page " counter(page) " of " counter(pages);
                    }
                }
            ''')
        ]
    )

    return response