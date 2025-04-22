from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.core.exceptions import ValidationError
import re

class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserRegistrationForm, self).__init__(*args, **kwargs)

        # Add class to form fields for consistent styling
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'password2'
        })

        # Update field labels
        self.fields['email'].label = "Email Address"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if the email is already in use
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Ensure that password1 and password2 match
        if password1 != password2:
            raise ValidationError("The two password fields must match.")
        
        # Validate password strength (optional)
        password_strength = self.check_password_strength(password1)
        if not password_strength:
            raise ValidationError("Password must contain at least 8 characters, including both letters and numbers.")

        return password2

    def check_password_strength(self, password):
        """ Check if the password contains at least one letter and one number, and is at least 8 characters long. """
        if len(password) < 8:
            return False
        if not re.search(r'[a-zA-Z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True



class ServiceRenderedForm(forms.ModelForm):
    class Meta:
        model = ServiceRendered
        fields = [
            'staff_name', 'amount', 'mode_of_payment', 'service_type',
            'service_rendered', 'description', 'staff_role',
            'customer_name', 'invoice_number', 'payment_status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'staff_name': forms.Select(attrs={'class': 'form-control'}),
            'mode_of_payment': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'service_rendered': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'staff_role': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceRenderedForm, self).__init__(*args, **kwargs)
        # Filter staff_name queryset
        self.fields['staff_name'].queryset = CustomUser.objects.filter(is_not_secretary=True)



class UniformForm(forms.ModelForm):
    class Meta:
        model = Uniform
        fields = ['uniform_date', 'uniform_type', 'uniform_color', 'uniform_notes']

        # Define widgets to customize form field styling
        widgets = {
            'uniform_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Use a date picker
            'uniform_type': forms.TextInput(attrs={'class': 'form-control'}),
            'uniform_color': forms.TextInput(attrs={'class': 'form-control'}),
            'uniform_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any notes here'}),
        }

    def __init__(self, *args, **kwargs):
        super(UniformForm, self).__init__(*args, **kwargs)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'category']

        # Define widgets to customize form field styling
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a description of the expense'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            # 'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        # You can customize the appearance or add placeholders if needed
        self.fields['amount'].widget.attrs['placeholder'] = 'Enter amount'
        self.fields['description'].widget.attrs['placeholder'] = 'Enter description'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        # self.fields['date'].widget.attrs['class'] = 'form-control'




class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'address', 'birthday', 'bio', 'facebook', 'twitter', 'instagram', 'linkedin']
        
        # Define widgets to customize form field styling
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write a short bio'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Facebook URL'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Twitter URL'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Instagram URL'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter your LinkedIn URL'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # You can customize the appearance or add placeholders if needed
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        self.fields['address'].widget.attrs['placeholder'] = 'Enter address'
        self.fields['birthday'].widget.attrs['placeholder'] = 'Select your birth date'
        self.fields['bio'].widget.attrs['placeholder'] = 'Add a short bio'
        self.fields['facebook'].widget.attrs['placeholder'] = 'Add your Facebook URL'
        self.fields['twitter'].widget.attrs['placeholder'] = 'Add your Twitter URL'
        self.fields['instagram'].widget.attrs['placeholder'] = 'Add your Instagram URL'
        self.fields['linkedin'].widget.attrs['placeholder'] = 'Add your LinkedIn URL'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter price'}),
            'uploaded_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # Allow partial updates


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name'
            }),
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your review here...'
            }),
        }


class SpaSessionBookingForm(forms.ModelForm):
    class Meta:
        model = SpaSessionBooking
        fields = ['session_type', 'service_type', 'preferred_date', 'preferred_time', 'message']

        widgets = {
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us anything special you need...', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(SpaSessionBookingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-control'


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'subject', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Last Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Subject',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type Message...',
                'rows': 5,
            }),
        }