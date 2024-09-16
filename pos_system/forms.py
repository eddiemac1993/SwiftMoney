# pos_system/forms.py

from django import forms
from .models import Shop

class ShopRegistrationForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'contact_info']

