from django import forms

from .models import Aadhar_Details


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Aadhar_Details
        exclude = ["number"]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "Phone_number": forms.NumberInput(attrs={"min": 1000000000, "max": 9999999999}),
            "pincode": forms.NumberInput(attrs={"min": 100000, "max": 999999}),
        }
