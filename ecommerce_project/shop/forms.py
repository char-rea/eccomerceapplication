"""Django forms for user registration, products, reviews, and stores."""

from django import forms
from .models import Profile, Product, Review, Store
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    """Form for registering a new user with a role."""

    role = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('vendor', 'Vendor')],
        widget=forms.Select
    )

    class Meta:
        """Metadata for UserRegisterForm."""
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    class Meta:
        """Metadata for UserRegisterForm."""
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    class Meta:
        """Metadata for UserRegisterForm."""
        model = User
        fields = ['username', 'email']

    def clean(self):
        """Validate matching passwords."""
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        """Save the user and associated profile."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )

        return user


class ProductForm(forms.ModelForm):
    """Form for creating or updating products."""

    class Meta:
        """Metadata for ProductForm."""
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'image',
            'available'
        ]


class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews."""

    class Meta:
        """Metadata for ReviewForm."""
        model = Review
        fields = ['rating', 'comment']


        """Django forms for basic user registration."""
        from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    """Form for registering a user with password confirmation."""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        """Ensure email address is unique."""
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def clean(self):
        """Validate that both passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        """Save the user instance with a hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user
    

class StoreForm(forms.ModelForm):
    """Form for creating or updating a store."""

    class Meta:
        """Metadata for StoreForm."""
        model = Store
        fields = ['name', 'description']