import uuid

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .i18n import tr
from .models import Account, Transaction
from .services import TransferError, open_account, transfer

PASSWORD = "Str0ng-Pass-9271!"


class TransferTests(TestCase):
    def setUp(self):
        cache.clear()
        self.a = open_account(User.objects.create_user("ali", password="x" * 12), "7391")
        self.b = open_account(User.objects.create_user("sara", password="x" * 12), "7391")

    def test_transfer_moves_money(self):
        transfer(sender=self.a, receiver_number=self.b.number, amount=100_000, description="", key=uuid.uuid4())
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual(self.a.balance, 900_000)
        self.assertEqual(self.b.balance, 1_100_000)

    def test_insufficient_funds(self):
        with self.assertRaises(TransferError):
            transfer(sender=self.a, receiver_number=self.b.number, amount=5_000_000, description="", key=uuid.uuid4())

    def test_self_transfer_and_negative(self):
        with self.assertRaises(TransferError):
            transfer(sender=self.a, receiver_number=self.a.number, amount=10, description="", key=uuid.uuid4())
        with self.assertRaises(TransferError):
            transfer(sender=self.a, receiver_number=self.b.number, amount=-10, description="", key=uuid.uuid4())

    def test_idempotent(self):
        key = uuid.uuid4()
        t1 = transfer(sender=self.a, receiver_number=self.b.number, amount=1000, description="", key=key)
        t2 = transfer(sender=self.a, receiver_number=self.b.number, amount=1000, description="", key=key)
        self.assertEqual(t1.pk, t2.pk)
        self.a.refresh_from_db()
        self.assertEqual(self.a.balance, 999_000)

    def test_ledger_immutable(self):
        tx = Transaction.objects.first()
        with self.assertRaises(PermissionError):
            tx.delete()


class ViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.alice = User.objects.create_user("alice", password=PASSWORD, first_name="Alice", last_name="Aa")
        self.bob = User.objects.create_user("bob", password=PASSWORD, first_name="Bob", last_name="Bb")
        self.a = open_account(self.alice, "7391")
        self.b = open_account(self.bob, "7391")

    def test_health(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_both_languages(self):
        fa = self.client.get(reverse("login"))
        self.assertContains(fa, 'lang="fa"')
        self.assertContains(fa, "ورود")
        self.client.cookies["simbank_lang"] = "en"
        en = self.client.get(reverse("login"))
        self.assertContains(en, 'lang="en"')
        self.assertContains(en, "Sign in")

    def test_language_switch_sets_cookie(self):
        r = self.client.post(reverse("set_language"), {"language": "en", "next": "/login/"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/login/")
        self.assertEqual(r.cookies["simbank_lang"].value, "en")

    def test_language_switch_blocks_open_redirect(self):
        r = self.client.post(reverse("set_language"), {"language": "fa", "next": "https://evil.example/"})
        self.assertEqual(r["Location"], "/")

    def test_login_and_dashboard(self):
        r = self.client.post(reverse("login"), {"username": "alice", "password": PASSWORD})
        self.assertEqual(r.status_code, 302)
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "1,000,000")

    def test_signup_creates_account(self):
        r = self.client.post(reverse("signup"), {
            "username": "newuser", "first_name": "New", "last_name": "User",
            "password1": PASSWORD, "password2": PASSWORD, "pin": "7391", "pin2": "7391",
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Account.objects.get(user__username="newuser").balance, 1_000_000)

    def test_full_transfer_flow(self):
        self.client.force_login(self.alice)
        r = self.client.post(reverse("transfer"), {"to_account": self.b.number, "amount": 250000, "description": "lunch"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(reverse("transfer_confirm")).status_code, 200)
        r = self.client.post(reverse("transfer_confirm"), {"pin": "7391"})
        tx = Transaction.objects.get(description="lunch")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("receipt", kwargs={"reference": tx.reference}))
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual(self.a.balance, 750_000)
        self.assertEqual(self.b.balance, 1_250_000)
        self.assertEqual(self.client.get(r["Location"]).status_code, 200)

    def test_wrong_pin_locks_after_three_attempts(self):
        self.client.force_login(self.alice)
        self.client.post(reverse("transfer"), {"to_account": self.b.number, "amount": 1000, "description": ""})
        for _ in range(3):
            self.assertEqual(self.client.post(reverse("transfer_confirm"), {"pin": "0001"}).status_code, 200)
        r = self.client.post(reverse("transfer_confirm"), {"pin": "7391"})
        self.assertEqual(r.status_code, 302)
        self.a.refresh_from_db()
        self.assertEqual(self.a.balance, 1_000_000)

    def test_receipt_hidden_from_strangers(self):
        tx = transfer(sender=self.a, receiver_number=self.b.number, amount=500, description="x", key=uuid.uuid4())
        carol = User.objects.create_user("carol", password=PASSWORD)
        open_account(carol, "7391")
        self.client.force_login(carol)
        self.assertEqual(self.client.get(reverse("receipt", kwargs={"reference": tx.reference})).status_code, 404)

    def test_transactions_page_both_languages(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse("transactions")).status_code, 200)
        self.client.cookies["simbank_lang"] = "en"
        r = self.client.get(reverse("transactions"))
        self.assertContains(r, "Transactions")


class I18nTests(TestCase):
    def test_translation_and_currency(self):
        with translation.override("en"):
            self.assertEqual(tr("cur"), "TMN")
            self.assertIn("TMN", tr("tr.available", amount="5"))
        with translation.override("fa"):
            self.assertEqual(tr("cur"), "تومان")
