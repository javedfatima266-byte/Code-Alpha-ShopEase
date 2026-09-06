from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Order


class UserRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your full name',
            'id': 'reg-full-name',
            'required': True,
        }),
        label="Full Name"
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username',
            'id': 'reg-username',
            'required': True,
        }),
        label="Username"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'reg-email',
            'required': True,
        }),
        label="Email Address"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a strong password (min 6 chars)',
            'id': 'reg-password',
            'required': True,
        }),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'id': 'reg-confirm-password',
            'required': True,
        }),
        label="Confirm Password"
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            if len(password) < 6:
                self.add_error('password', "Password must be at least 6 characters long.")
        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email',
            'id': 'login-username',
            'required': True,
        }),
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'login-password',
            'required': True,
        }),
        label="Password"
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'login-remember',
        }),
        label="Remember me"
    )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-first-name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-last-name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'id': 'profile-email'})
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-phone', 'placeholder': '+1 (555) 000-0000'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-address', 'placeholder': 'Street address'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-city', 'placeholder': 'City'})
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-postal-code', 'placeholder': 'Zip / Postal code'})
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


class CheckoutForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter full name for delivery',
            'id': 'checkout-full-name',
            'required': True,
        }),
        label="Recipient Full Name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Order confirmation will be sent here',
            'id': 'checkout-email',
            'required': True,
        }),
        label="Email Address"
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contact phone for delivery',
            'id': 'checkout-phone',
            'required': True,
        }),
        label="Phone Number"
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Street address, apartment, suite, etc.',
            'id': 'checkout-address',
            'required': True,
        }),
        label="Street Address"
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'City / Town',
            'id': 'checkout-city',
            'required': True,
        }),
        label="City"
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Postal code / ZIP',
            'id': 'checkout-postal-code',
            'required': True,
        }),
        label="Postal Code"
    )
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        initial=Order.PAYMENT_COD,
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio',
            'id': 'checkout-payment-method',
        }),
        label="Payment Method"
    )

    class Meta:
        model = Order
        fields = [
            'full_name',
            'email',
            'phone',
            'address',
            'city',
            'postal_code',
            'payment_method',
        ]
