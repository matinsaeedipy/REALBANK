import uuid
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from . import security
from .i18n import tr, tr_lazy
from .forms import ConfirmForm, SignUpForm, TransferForm
from .models import Account, Transaction
from .services import TransferError, transfer

LOGIN_LIMIT, LOGIN_WINDOW = 5, 15 * 60
PIN_LIMIT, PIN_WINDOW = 3, 15 * 60
LOOKUP_LIMIT, LOOKUP_WINDOW = 20, 60 * 60
SIGNUP_LIMIT, SIGNUP_WINDOW = 5, 60 * 60


def account_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            request.account = request.user.account
        except ObjectDoesNotExist:
            return HttpResponseForbidden(tr("m.no_account"))
        return view(request, *args, **kwargs)
    return wrapper


def _annotate(transactions, account):
    for t in transactions:
        t.is_out = t.sender_id == account.pk
        other = t.receiver if t.is_out else t.sender
        t.other_name = other.display_name if other else tr("tx.bank")
        t.other_initial = t.other_name[:1]
        t.title = t.other_name if (t.is_out or t.sender_id) else tr("tx.opening")
        t.balance_after = t.sender_balance_after if t.is_out else t.receiver_balance_after
    return transactions


class BankLoginView(LoginView):
    template_name = "bank/login.html"
    redirect_authenticated_user = True

    def _keys(self, request):
        username = request.POST.get("username", "").strip().lower()[:150]
        return f"login:ip:{security.client_ip(request)}", f"login:user:{username}"

    def post(self, request, *args, **kwargs):
        ip_key, user_key = self._keys(request)
        if security.is_blocked(ip_key, LOGIN_LIMIT * 3) or security.is_blocked(user_key, LOGIN_LIMIT):
            messages.error(request, tr("m.login_locked"))
            return redirect("login")
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        ip_key, user_key = self._keys(self.request)
        security.hit(ip_key, LOGIN_WINDOW)
        security.hit(user_key, LOGIN_WINDOW)
        return super().form_invalid(form)

    def form_valid(self, form):
        ip_key, user_key = self._keys(self.request)
        security.clear(user_key)
        return super().form_valid(form)


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    key = f"signup:{security.client_ip(request)}"
    form = SignUpForm(request.POST or None)
    if request.method == "POST":
        if security.is_blocked(key, SIGNUP_LIMIT):
            messages.error(request, tr("m.signup_limited"))
        elif form.is_valid():
            security.hit(key, SIGNUP_WINDOW)
            user = form.save()
            login(request, user)
            messages.success(request, tr("m.signup_ok"))
            return redirect("dashboard")
    return render(request, "bank/signup.html", {"form": form})


def _group_by_day(items):
    today = timezone.localdate()
    groups = []
    for t in items:
        d = timezone.localtime(t.created_at).date()
        if not groups or groups[-1]["date"] != d:
            if d == today:
                label = tr("day.today")
            elif d == today - timedelta(days=1):
                label = tr("day.yesterday")
            else:
                label = d.strftime("%Y/%m/%d")
            groups.append({"date": d, "label": label, "items": []})
        groups[-1]["items"].append(t)
    return groups


def _sparkline(account, width=300, height=100, pad=8):
    """نمودار روند موجودی از روی «موجودی پس از تراکنش» ۳۰ تراکنش آخر."""
    rows = list(account.transactions()[:30])[::-1]
    values = [
        t.sender_balance_after if t.sender_id == account.pk else t.receiver_balance_after
        for t in rows
    ] or [account.balance]
    if len(values) == 1:
        values = values * 2
    lo, hi = min(values), max(values)
    step = width / (len(values) - 1)

    def y_of(v):
        if hi == lo:
            return height / 2
        return pad + (hi - v) / (hi - lo) * (height - 2 * pad)

    pts = [(round(i * step, 1), round(y_of(v), 1)) for i, v in enumerate(values)]
    d = f"M{pts[0][0]},{pts[0][1]}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cx = round((x0 + x1) / 2, 1)
        d += f" C{cx},{y0} {cx},{y1} {x1},{y1}"
    area = f"{d} L{pts[-1][0]},{height} L{pts[0][0]},{height} Z"
    return {"line": d, "area": area, "end_x": pts[-1][0], "end_y": pts[-1][1]}


@account_required
def dashboard(request):
    account = request.account
    recent = _annotate(list(account.transactions()[:6]), account)

    since = timezone.now() - timedelta(days=30)
    last30 = list(account.transactions().filter(created_at__gte=since))
    income = sum(t.amount for t in last30 if t.receiver_id == account.pk and t.sender_id)
    expense = sum(t.amount for t in last30 if t.sender_id == account.pk)
    net = income - expense

    contacts, seen = [], set()
    for t in account.sent.select_related("receiver__user").order_by("-created_at")[:40]:
        if t.receiver_id not in seen:
            seen.add(t.receiver_id)
            contacts.append(t.receiver)
        if len(contacts) == 6:
            break

    return render(request, "bank/dashboard.html", {
        "account": account, "recent": recent, "income": income, "expense": expense,
        "net": net, "net_abs": abs(net), "spark": _sparkline(account), "contacts": contacts,
    })


@account_required
@require_http_methods(["GET", "POST"])
def transfer_start(request):
    account = request.account
    prefill = request.GET.get("to", "")
    initial = {"to_account": prefill} if prefill.isdigit() and len(prefill) == 10 else None
    form = TransferForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        key = f"lookup:{request.user.pk}"
        if security.is_blocked(key, LOOKUP_LIMIT):
            messages.error(request, tr("m.lookup_limited"))
            return redirect("transfer")
        security.hit(key, LOOKUP_WINDOW)

        to_number, amount = form.cleaned_data["to_account"], form.cleaned_data["amount"]
        receiver = Account.objects.filter(number=to_number).select_related("user").first()
        if receiver is None:
            form.add_error("to_account", tr("e.acct_not_found"))
        elif receiver.pk == account.pk:
            form.add_error("to_account", tr("e.self"))
        elif amount > account.balance:
            form.add_error("amount", tr("e.insufficient"))
        else:
            request.session["pending_transfer"] = {
                "to": to_number,
                "amount": amount,
                "description": form.cleaned_data["description"],
                "key": str(uuid.uuid4()),
            }
            return redirect("transfer_confirm")
    return render(request, "bank/transfer.html", {"form": form, "account": account})


@account_required
@require_http_methods(["GET", "POST"])
def transfer_confirm(request):
    account = request.account
    pending = request.session.get("pending_transfer")
    if not pending:
        return redirect("transfer")
    receiver = get_object_or_404(Account.objects.select_related("user"), number=pending["to"])
    form = ConfirmForm(request.POST or None)
    pin_key = f"pin:{request.user.pk}"

    if request.method == "POST":
        if security.is_blocked(pin_key, PIN_LIMIT):
            request.session.pop("pending_transfer", None)
            messages.error(request, tr("m.pin_locked"))
            return redirect("dashboard")
        if form.is_valid():
            if not account.check_pin(form.cleaned_data["pin"]):
                security.hit(pin_key, PIN_WINDOW)
                form.add_error("pin", tr("e.pin_wrong"))
            else:
                try:
                    tx = transfer(
                        sender=account,
                        receiver_number=pending["to"],
                        amount=pending["amount"],
                        description=pending["description"],
                        key=uuid.UUID(pending["key"]),
                    )
                except TransferError as exc:
                    request.session.pop("pending_transfer", None)
                    messages.error(request, str(exc))
                    return redirect("transfer")
                security.clear(pin_key)
                request.session.pop("pending_transfer", None)
                return redirect("receipt", reference=tx.reference)

    return render(request, "bank/confirm.html", {
        "form": form, "pending": pending, "receiver": receiver, "account": account,
        "remaining": account.balance - pending["amount"],
    })


@account_required
def transactions(request):
    kind = request.GET.get("type", "all")
    qs = request.account.transactions()
    if kind == "in":
        qs = qs.filter(receiver=request.account)
    elif kind == "out":
        qs = qs.filter(sender=request.account)
    page = Paginator(qs, 12).get_page(request.GET.get("page"))
    items = _annotate(list(page.object_list), request.account)
    return render(request, "bank/transactions.html", {
        "page": page, "groups": _group_by_day(items), "kind": kind, "account": request.account,
    })


@account_required
def receipt(request, reference):
    account = request.account
    tx = get_object_or_404(
        Transaction.objects.select_related("sender__user", "receiver__user"),
        Q(sender=account) | Q(receiver=account),
        reference=reference,
    )
    return render(request, "bank/receipt.html", {"tx": tx, "account": account, "is_out": tx.sender_id == account.pk})


class BankPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = "bank/password_change.html"
    success_url = reverse_lazy("dashboard")
    success_message = tr_lazy("m.pw_changed")


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


@require_POST
def set_language(request):
    lang = request.POST.get("language")
    if lang not in ("fa", "en"):
        lang = "fa"
    target = request.POST.get("next", "/")
    if not url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        target = "/"
    response = redirect(target)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME, lang, max_age=365 * 24 * 3600,
        samesite="Lax", secure=settings.SESSION_COOKIE_SECURE,
    )
    return response
