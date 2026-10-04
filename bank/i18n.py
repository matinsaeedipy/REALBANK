"""ترجمه‌ی دوزبانه (فارسی / English) بدون نیاز به فایل‌های gettext."""
from django.utils import translation
from django.utils.functional import lazy

LANGS = ("fa", "en")

# کلید: (فارسی, English)
STRINGS = {
    # ---- عمومی ----
    "brand": ("سیم‌بانک", "SimBank"),
    "cur": ("تومان", "TMN"),
    "lang.other_value": ("en", "fa"),
    "lang.other_code": ("EN", "فا"),
    "lang.other_name": ("English", "فارسی"),
    "nav.home": ("خانه", "Home"),
    "nav.transfer": ("انتقال", "Transfer"),
    "nav.transactions": ("تراکنش‌ها", "Transactions"),
    "nav.security": ("امنیت", "Security"),
    "nav.aria": ("منوی اصلی", "Main menu"),
    "top.hello": ("سلام", "Hello"),
    "top.theme": ("تغییر تم روشن/تیره", "Toggle light/dark theme"),
    "top.logout": ("خروج از حساب", "Sign out"),
    "msg.close": ("بستن", "Close"),
    "sim.note": ("", ""),

    # ---- ورود ----
    "login.title": ("ورود", "Sign in"),
    "login.h1a": ("پولت را", "Move your money"),
    "login.h1b": ("هوشمند", "smarter"),
    "login.h1c": ("جابه‌جا کن", ""),
    "login.sub": ("--------------------------------------",
                  "-----------------------------------"),
    "login.li1": ("انتقال فوری با رسید رسمی", "Instant transfers with official receipts"),
    "login.li2": ("تأیید هر انتقال با رمز تراکنش", "Every transfer confirmed with a transaction PIN"),
    "login.heading": ("ورود به حساب", "Sign in to your account"),
    "login.submit": ("ورود", "Sign in"),
    "login.noacct": ("حساب ندارید؟", "No account yet?"),
    "login.signup_link": ("افتتاح حساب", "Open an account"),

    # ---- ثبت‌نام ----
    "signup.title": ("افتتاح حساب", "Open an account"),
    "signup.h1a": ("در یک دقیقه", "Open an account"),
    "signup.h1b": ("حساب", "in one minute"),
    "signup.h1c": ("باز کن", ""),
    "signup.sub": ("بعد از ثبت‌نام، یک شماره حساب ۱۰ رقمی و موجودی اولیه‌ دریافت می‌کنی.",
                   "After signing up you get a 10-digit account number starting balance."),
    "signup.li1": ("رمز عبور حداقل ۱۰ کاراکتر", "Password of at least 10 characters"),
    "signup.li2": ("رمز تراکنش ۴ رقمی برای هر انتقال", "A 4-digit transaction PIN for every transfer"),
    "signup.heading": ("افتتاح حساب", "Open an account"),
    "signup.submit": ("افتتاح حساب", "Create account"),
    "signup.haveacct": ("قبلاً ثبت‌نام کرده‌اید؟", "Already have an account?"),
    "signup.login_link": ("ورود", "Sign in"),

    # ---- داشبورد ----
    "dash.total": ("موجودی کل", "Total balance"),
    "dash.last30": ("در ۳۰ روز اخیر", "in the last 30 days"),
    "dash.send": ("انتقال", "Send"),
    "dash.account_no": ("شماره حساب", "Account no."),
    "dash.history": ("تراکنش‌ها", "History"),
    "dash.chart": ("روند موجودی", "Balance trend"),
    "dash.copy_title": ("کپی شماره حساب", "Copy account number"),
    "dash.in30": ("دریافتی ۳۰ روز", "Received (30 days)"),
    "dash.out30": ("پرداختی ۳۰ روز", "Sent (30 days)"),
    "dash.quick": ("انتقال سریع", "Quick send"),
    "dash.new": ("جدید", "New"),
    "dash.quick_empty": ("بعد از اولین انتقال، گیرنده‌های اخیرت اینجا می‌آیند. شماره حساب خودت را کپی کن و به دوستت بده تا برایت پول بفرستد.",
                         "Your recent recipients will appear here after your first transfer. Copy your account number and share it to receive money."),
    "dash.recent": ("آخرین تراکنش‌ها", "Recent transactions"),
    "dash.all": ("همه", "All"),

    # ---- تراکنش‌ها ----
    "tx.empty": ("هنوز تراکنشی ندارید. اولین انتقال را از بخش «انتقال» انجام دهید.",
                 "No transactions yet. Make your first transfer from the Transfer tab."),
    "tx.bank": ("بانک", "Bank"),
    "tx.opening": ("هدیه‌ی افتتاح حساب", "Welcome bonus"),
    "txs.title": ("تراکنش‌ها", "Transactions"),
    "txs.all": ("همه", "All"),
    "txs.in": ("دریافتی", "Received"),
    "txs.out": ("پرداختی", "Sent"),
    "txs.none": ("تراکنشی برای نمایش وجود ندارد.", "No transactions to show."),
    "txs.prev": ("قبلی", "Previous"),
    "txs.next": ("بعدی", "Next"),
    "txs.page": ("صفحه {n} از {total}", "Page {n} of {total}"),
    "day.today": ("امروز", "Today"),
    "day.yesterday": ("دیروز", "Yesterday"),

    # ---- انتقال ----
    "tr.title": ("انتقال وجه", "Transfer money"),
    "step.info": ("اطلاعات", "Details"),
    "step.confirm": ("تأیید", "Confirm"),
    "step.receipt": ("رسید", "Receipt"),
    "tr.how_much": ("چقدر می‌فرستی؟", "How much do you want to send?"),
    "tr.available": ("موجودی قابل انتقال: {amount} {cur}", "Available to transfer: {amount} {cur}"),
    "tr.continue": ("ادامه", "Continue"),
    "tr.chips": ("مبلغ‌های پیشنهادی", "Suggested amounts"),

    # ---- تأیید ----
    "cf.title": ("تأیید انتقال", "Confirm transfer"),
    "cf.you": ("شما", "You"),
    "cf.to_acct": ("شماره حساب مقصد", "Recipient account"),
    "cf.desc": ("توضیحات", "Description"),
    "cf.after": ("موجودی پس از انتقال", "Balance after transfer"),
    "cf.submit": ("تأیید و انتقال", "Confirm & send"),
    "cf.edit": ("ویرایش", "Edit"),

    # ---- رسید ----
    "rc.title": ("رسید تراکنش", "Transaction receipt"),
    "rc.sent": ("انتقال با موفقیت انجام شد", "Transfer completed"),
    "rc.received": ("واریز به حساب شما", "Deposit to your account"),
    "rc.ref": ("شماره پیگیری", "Reference no."),
    "rc.when": ("تاریخ و ساعت", "Date & time"),
    "rc.from": ("از", "From"),
    "rc.to": ("به", "To"),
    "rc.desc": ("توضیحات", "Description"),
    "rc.after": ("موجودی پس از تراکنش", "Balance after transaction"),
    "rc.home": ("بازگشت به خانه", "Back to home"),
    "rc.print": ("چاپ", "Print"),

    # ---- امنیت ----
    "sec.title": ("امنیت", "Security"),
    "sec.heading": ("تغییر رمز عبور", "Change password"),
    "sec.submit": ("ذخیره‌ی رمز جدید", "Save new password"),

    # ---- فرم‌ها ----
    "f.first": ("نام", "First name"),
    "f.last": ("نام خانوادگی", "Last name"),
    "f.pin_new": ("رمز تراکنش (۴ رقم)", "Transaction PIN (4 digits)"),
    "f.pin_help": ("برای تأیید هر انتقال لازم است.", "Required to confirm every transfer."),
    "f.pin2": ("تکرار رمز تراکنش", "Repeat transaction PIN"),
    "f.to_account": ("شماره حساب مقصد", "Recipient account number"),
    "f.amount": ("مبلغ ({cur})", "Amount ({cur})"),
    "f.description": ("توضیحات (اختیاری)", "Description (optional)"),
    "f.pin": ("رمز تراکنش", "Transaction PIN"),

    # ---- خطاها ----
    "e.acct_format": ("شماره حساب باید ۱۰ رقم باشد.", "Account number must be 10 digits."),
    "e.pin_digits": ("رمز تراکنش باید دقیقاً ۴ رقم باشد.", "The PIN must be exactly 4 digits."),
    "e.pin_weak": ("این رمز بیش از حد ساده است.", "This PIN is too simple."),
    "e.pin_mismatch": ("رمزهای تراکنش یکسان نیستند.", "The PINs do not match."),
    "e.pin_wrong": ("رمز تراکنش اشتباه است.", "Incorrect PIN."),
    "e.acct_not_found": ("حساب مقصد یافت نشد.", "Recipient account not found."),
    "e.self": ("نمی‌توانید به حساب خودتان انتقال دهید.", "You can't transfer to your own account."),
    "e.insufficient": ("موجودی حساب کافی نیست.", "Insufficient balance."),
    "e.amount_invalid": ("مبلغ نامعتبر است.", "Invalid amount."),
    "e.max_single": ("مبلغ از سقف هر انتقال بیشتر است.", "Amount exceeds the per-transfer limit."),
    "e.daily": ("سقف انتقال روزانه‌ی شما تکمیل می‌شود.", "This would exceed your daily transfer limit."),

    # ---- پیام‌ها ----
    "m.login_locked": ("تلاش‌های ناموفق زیاد بود. ۱۵ دقیقه بعد دوباره امتحان کنید.",
                       "Too many failed attempts. Please try again in 15 minutes."),
    "m.signup_limited": ("تعداد ثبت‌نام‌ها از این دستگاه زیاد بود. بعداً امتحان کنید.",
                         "Too many sign-ups from this device. Please try later."),
    "m.signup_ok": ("حساب شما ساخته شد و موجودی اولیه واریز شد.",
                    "Your account is ready and the starting balance has been credited."),
    "m.lookup_limited": ("تعداد درخواست‌ها زیاد بود. بعداً دوباره امتحان کنید.",
                         "Too many requests. Please try again later."),
    "m.pin_locked": ("رمز تراکنش چند بار اشتباه وارد شد. ۱۵ دقیقه بعد امتحان کنید.",
                     "The PIN was entered incorrectly too many times. Try again in 15 minutes."),
    "m.pw_changed": ("رمز عبور با موفقیت تغییر کرد.", "Your password was changed successfully."),
    "m.no_account": ("این کاربر حساب بانکی ندارد.", "This user has no bank account."),
}


def current_lang():
    code = (translation.get_language() or "fa").lower()
    return "fa" if code.startswith("fa") else "en"


def tr(key, **kwargs):
    fa, en = STRINGS[key]
    text = fa if current_lang() == "fa" else en
    kwargs.setdefault("cur", STRINGS["cur"][0] if current_lang() == "fa" else STRINGS["cur"][1])
    return text.format(**kwargs)


tr_lazy = lazy(tr, str)
