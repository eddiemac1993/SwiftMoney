# pos_system/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Shop, Product
from .forms import ShopRegistrationForm

def shop_list(request):
    shops = Shop.objects.filter(is_approved=True)
    return render(request, 'pos_system/shop_list.html', {'shops': shops})

@login_required
def register_shop(request):
    if request.method == 'POST':
        form = ShopRegistrationForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            return redirect('shop_waiting_approval')
    else:
        form = ShopRegistrationForm()
    return render(request, 'pos_system/register_shop.html', {'form': form})

@login_required
def shop_waiting_approval(request):
    return render(request, 'pos_system/shop_waiting_approval.html')
