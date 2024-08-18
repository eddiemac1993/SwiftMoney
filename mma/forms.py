from django import forms
from .models import FloatRequest, CashRequest

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
    