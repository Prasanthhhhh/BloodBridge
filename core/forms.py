
from django import forms
from .models import DonorProfile, VolunteerProfile


class DonorRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full Name")
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    phone = forms.CharField(max_length=15, label="Phone Number")
    blood_group = forms.ChoiceField(
        choices=DonorProfile.BLOOD_GROUPS,
        label="Blood Group"
    )
    city = forms.CharField(max_length=100, label="City")


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ['full_name', 'phone', 'blood_group', 'city']

        labels = {
            'full_name': 'Full Name',
            'phone': 'Phone Number',
            'blood_group': 'Blood Group',
            'city': 'City',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Enter your city'
            }),
        }


class VolunteerRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        label="Full Name"
    )
    username = forms.CharField(
        max_length=150,
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    phone = forms.CharField(
        max_length=15,
        label="Phone Number"
    )
    city = forms.CharField(
        max_length=100,
        label="City"
    )

from .models import BloodRequest


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'patient_name',
            'contact_phone',
            'blood_group',
            'city',
            'hospital_name',
            'units_needed',
            'urgency',
            'details',
        ]

        widgets = {
            'patient_name': forms.TextInput(
                attrs={'placeholder': 'Patient name'}
            ),
            'contact_phone': forms.TextInput(
                attrs={'placeholder': 'Contact phone number'}
            ),
            'city': forms.TextInput(
                attrs={'placeholder': 'City'}
            ),
            'hospital_name': forms.TextInput(
                attrs={'placeholder': 'Hospital name'}
            ),
            'units_needed': forms.NumberInput(
                attrs={'min': 1, 'max': 100}
            ),
            'details': forms.Textarea(
                attrs={
                    'placeholder': 'Additional details (optional)',
                    'rows': 4,
                }
            ),
        }

