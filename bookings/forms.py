from django import forms
from django.contrib.auth.models import User
from .models import Booking


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = [
            'car_model',
            'car_number',
            'airport',
            'parking_date',
            'return_date',
            'service_type'
        ]

        widgets = {
            'parking_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):

        cleaned_data = super().clean()

        parking_date = cleaned_data.get("parking_date")
        return_date = cleaned_data.get("return_date")

        if parking_date and return_date:

            if return_date < parking_date:
                raise forms.ValidationError(
                    "Return date must be after the parking date."
                )

        return cleaned_data