import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import bank.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(default=bank.models.generate_account_number, max_length=10, unique=True)),
                ("balance", models.PositiveBigIntegerField(default=0)),
                ("pin_hash", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(default=bank.models.generate_reference, max_length=12, unique=True)),
                ("amount", models.PositiveBigIntegerField()),
                ("description", models.CharField(blank=True, max_length=100)),
                ("idempotency_key", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("sender_balance_after", models.PositiveBigIntegerField(blank=True, null=True)),
                ("receiver_balance_after", models.PositiveBigIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("receiver", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="received", to="bank.account")),
                ("sender", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="sent", to="bank.account")),
            ],
        ),
        migrations.AddConstraint(
            model_name="account",
            constraint=models.CheckConstraint(condition=models.Q(("balance__gte", 0)), name="balance_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="transaction",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="amount_positive"),
        ),
        migrations.AddConstraint(
            model_name="transaction",
            constraint=models.CheckConstraint(condition=models.Q(("sender", models.F("receiver")), _negated=True), name="no_self_transfer"),
        ),
    ]
