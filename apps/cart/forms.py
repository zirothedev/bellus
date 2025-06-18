from django import forms
import re

class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'required': 'required'
        })
    )

    
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'required': 'required'
        })
    )

    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': 'required'
        })
    )

    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'required': 'required'
        })
    )

    
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your street address',
            'required': 'required'
        })
    )

    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city',
            'required': 'required'
        })
    )

    
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your state/province',
            'required': 'required'
        })
    )

    
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ZIP/postal code',
            'required': 'required'
        })
    )

    
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your country',
            'required': 'required'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        raise forms.ValidationError('Email is required.')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower() if email else email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        cleaned_phone = re.sub(r'\D', '', phone)
        if len(cleaned_phone) < 10:
            raise forms.ValidationError('Please enter a valid phone number.')
        return cleaned_phone
    
        return zip_code
class CartAddProductForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)  # Hidden field for product ID
    quantity = forms.IntegerField(min_value=1, initial=1)  # Field for quantity

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity