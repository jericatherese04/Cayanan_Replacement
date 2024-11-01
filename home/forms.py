from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Full Name"
    )
    contact_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Contact Number"
    )
    company_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Company Name"
    )
    business_title = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Business Title"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'full_name', 'contact_number', 'company_name',
                  'business_title']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # You can add more validation checks here if needed

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data.get("full_name"),
                contact_number=self.cleaned_data.get("contact_number"),
                company_name=self.cleaned_data.get("company_name"),
                business_title=self.cleaned_data.get("business_title")
            )

        return user
