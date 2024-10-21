from django import forms
from .models import FloatRequest, CashRequest
from django import forms
from .models import Order
# mma/forms.py
from django import forms
from .models import Refund

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['order']  # Exclude 'amount' as it's auto-calculated

# In forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'delivery_time', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'delivery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None

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
