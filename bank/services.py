from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .i18n import tr
from .models import Account, Transaction


class TransferError(Exception):
    pass


@transaction.atomic
def open_account(user, pin):
    account = Account(user=user)
    account.set_pin(pin)
    account.save()
    bonus = settings.OPENING_BALANCE
    Account.objects.filter(pk=account.pk).update(balance=bonus)
    Transaction.objects.create(
        sender=None,
        receiver=account,
        amount=bonus,
        description="Welcome bonus",
        receiver_balance_after=bonus,
    )
    return account


@transaction.atomic
def transfer(*, sender, receiver_number, amount, description, key):
    """انتقال اتمی پول. به‌روزرسانی شرطی با F() جلوی race condition و موجودی منفی را می‌گیرد."""
    existing = Transaction.objects.filter(idempotency_key=key).first()
    if existing:  # ارسال دوباره‌ی همان فرم، تراکنش تکراری نمی‌سازد
        return existing

    if not isinstance(amount, int) or amount <= 0:
        raise TransferError(tr("e.amount_invalid"))
    if amount > settings.MAX_SINGLE_TRANSFER:
        raise TransferError(tr("e.max_single"))

    try:
        receiver = Account.objects.get(number=receiver_number)
    except Account.DoesNotExist:
        raise TransferError(tr("e.acct_not_found"))
    if receiver.pk == sender.pk:
        raise TransferError(tr("e.self"))

    start_of_day = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    sent_today = (
        Transaction.objects.filter(sender=sender, created_at__gte=start_of_day)
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    if sent_today + amount > settings.DAILY_TRANSFER_LIMIT:
        raise TransferError(tr("e.daily"))

    debited = Account.objects.filter(pk=sender.pk, balance__gte=amount).update(balance=F("balance") - amount)
    if not debited:
        raise TransferError(tr("e.insufficient"))
    Account.objects.filter(pk=receiver.pk).update(balance=F("balance") + amount)

    sender_balance = Account.objects.values_list("balance", flat=True).get(pk=sender.pk)
    receiver_balance = Account.objects.values_list("balance", flat=True).get(pk=receiver.pk)
    return Transaction.objects.create(
        sender=sender,
        receiver=receiver,
        amount=amount,
        description=description,
        idempotency_key=key,
        sender_balance_after=sender_balance,
        receiver_balance_after=receiver_balance,
    )
