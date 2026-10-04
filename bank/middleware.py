from django.conf import settings
from django.utils import translation

CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
    "frame-ancestors 'none'; form-action 'self'; base-uri 'self'; object-src 'none'"
)


class LanguageMiddleware:
    """زبان از کوکی خوانده می‌شود؛ پیش‌فرض فارسی است."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if lang not in ("fa", "en"):
            lang = "fa"
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)
        return response


class SecurityHeadersMiddleware:
    """هدرهای امنیتی: CSP سخت‌گیرانه، جلوگیری از کش صفحات حساس، محدودیت مجوزها."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/manage-bank-admin/"):
            response.headers.setdefault("Content-Security-Policy", CSP)
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"
        if not request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, private"
        return response
