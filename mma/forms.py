from django import forms
from .models import FloatRequest, CashRequest
from .models import Order
from .models import Refund
from .models import QuizScore
from .models import BirthdayWish
from .models import RideRequest, Review

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = ['username', 'phone_number', 'pickup_location', 'destination', 'amount']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number',
                'required': True,
                'type': 'tel'
            }),
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'From (Your Location)',
                'required': True
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'To (Destination)',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Proposed Amount (ZMW)',
                'required': True
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating']
class BirthdayWishForm(forms.ModelForm):
    class Meta:
        model = BirthdayWish
        fields = ['sender_name', 'recipient_name', 'age', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class SubmitScoreForm(forms.ModelForm):
    class Meta:
        model = QuizScore
        fields = ['username', 'phone_number']  # Include username
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Enter your username',
                'class': 'form-control',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'class': 'form-control',
            }),
        }


class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['order']  # Exclude 'amount' as it's auto-calculated

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'store_address', 'price',
            'delivery_time', 'image', 'stock_count', 'phone_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'store_address': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'delivery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': 'Enter initial stock quantity'
            }),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None
        self.fields['stock_count'].help_text = 'Enter the initial quantity available in stock'
        self.fields['stock_count'].required = True

    def clean_stock_count(self):
        stock_count = self.cleaned_data.get('stock_count')
        if stock_count is not None and stock_count < 0:
            raise forms.ValidationError("Stock count cannot be negative.")
        return stock_count

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone_number']

class FloatRequestForm(forms.ModelForm):
    class Meta:
        model = FloatRequest
        fields = ['amount', 'service']

class CashRequestForm(forms.ModelForm):
    class Meta:
        model = CashRequest
        fields = ['amount']

class BalanceUpdateForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = forms.ChoiceField(choices=[('cash', 'Cash'), ('float', 'Float')])
    service = forms.ChoiceField(choices=FloatRequest.SERVICES, required=False)

# mma/forms.py

from django import forms

class ReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    user = forms.ChoiceField(choices=[(None, 'All Users')], required=False)  # Adjust this as needed

    def __init__(self, *args, **kwargs):
        user_choices = kwargs.pop('user_choices', None)
        super().__init__(*args, **kwargs)
        if user_choices:
            self.fields['user'].choices += user_choices
