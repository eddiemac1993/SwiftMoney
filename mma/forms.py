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



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name']

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
