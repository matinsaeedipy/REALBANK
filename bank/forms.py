import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .i18n import tr_lazy
from .services import open_account

WEAK_PINS = {"0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999", "1234", "4321", "1212"}


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=tr_lazy("f.first"), max_length=30)
    last_name = forms.CharField(label=tr_lazy("f.last"), max_length=30)
    pin = forms.CharField(
        label=tr_lazy("f.pin_new"), max_length=4, min_length=4,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
        help_text=tr_lazy("f.pin_help"),
    )
    pin2 = forms.CharField(
        label=tr_lazy("f.pin2"), max_length=4, min_length=4,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")

    def clean_pin(self):
        pin = self.cleaned_data["pin"]
        if not re.fullmatch(r"\d{4}", pin):
            raise forms.ValidationError(tr_lazy("e.pin_digits"))
        if pin in WEAK_PINS:
            raise forms.ValidationError(tr_lazy("e.pin_weak"))
        return pin

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("pin") and cleaned.get("pin") != cleaned.get("pin2"):
            self.add_error("pin2", tr_lazy("e.pin_mismatch"))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=True)
        open_account(user, self.cleaned_data["pin"])
        return user


class TransferForm(forms.Form):
    to_account = forms.RegexField(
        regex=r"^\d{10}$", label=tr_lazy("f.to_account"), max_length=10,
        error_messages={"invalid": tr_lazy("e.acct_format")},
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off", "dir": "ltr"}),
    )
    amount = forms.IntegerField(
        label=tr_lazy("f.amount"), min_value=1,
        widget=forms.NumberInput(attrs={
            "inputmode": "numeric", "autocomplete": "off", "dir": "ltr",
            "placeholder": "0", "class": "amount-input",
        }),
    )
    description = forms.CharField(label=tr_lazy("f.description"), max_length=100, required=False)


class ConfirmForm(forms.Form):
    pin = forms.CharField(
        label=tr_lazy("f.pin"), max_length=4, min_length=4,
        widget=forms.PasswordInput(attrs={
            "inputmode": "numeric", "autocomplete": "off", "dir": "ltr",
            "placeholder": "••••", "class": "pin-input",
        }),
    )
