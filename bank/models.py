import secrets
import string
import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.db.models import F, Q


def generate_account_number():
    while True:
        number = str(secrets.randbelow(9) + 1) + "".join(
            str(secrets.randbelow(10)) for _ in range(9)
        )
        if not Account.objects.filter(number=number).exists():
            return number


def generate_reference():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        ref = "TRX" + "".join(secrets.choice(alphabet) for _ in range(9))
        if not Transaction.objects.filter(reference=ref).exists():
            return ref


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    number = models.CharField(max_length=10, unique=True, default=generate_account_number)
    balance = models.PositiveBigIntegerField(default=0)
    pin_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(balance__gte=0), name="balance_non_negative")]

    def __str__(self):
        return f"{self.number} ({self.user.username})"

    def set_pin(self, raw_pin):
        self.pin_hash = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin_hash)

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def masked_name(self):
        """نام با پنهان‌سازی بخشی از آن، مثل بانک‌های واقعی."""
        parts = self.display_name.split()
        return " ".join(p[0] + "•" * min(len(p) - 1, 4) if len(p) > 1 else p for p in parts)

    @property
    def formatted_number(self):
        n = self.number
        return f"{n[:4]} {n[4:8]} {n[8:]}"

    def transactions(self):
        return (
            Transaction.objects.filter(Q(sender=self) | Q(receiver=self))
            .select_related("sender__user", "receiver__user")
            .order_by("-created_at")
        )


class Transaction(models.Model):
    """دفتر کل تغییرناپذیر: هر تراکنش پس از ثبت قابل ویرایش یا حذف نیست."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=12, unique=True, default=generate_reference)
    sender = models.ForeignKey(Account, null=True, blank=True, on_delete=models.PROTECT, related_name="sent")
    receiver = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="received")
    amount = models.PositiveBigIntegerField()
    description = models.CharField(max_length=100, blank=True)
    idempotency_key = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    sender_balance_after = models.PositiveBigIntegerField(null=True, blank=True)
    receiver_balance_after = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="amount_positive"),
            models.CheckConstraint(condition=~Q(sender=F("receiver")), name="no_self_transfer"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("تراکنش ثبت‌شده قابل ویرایش نیست.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("تراکنش ثبت‌شده قابل حذف نیست.")

    def __str__(self):
        return self.reference
