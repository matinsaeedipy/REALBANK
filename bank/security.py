"""محدودسازی تلاش‌ها (ضد حمله‌ی حدس رمز) بدون نیاز به کتابخانه‌ی خارجی."""
from django.core.cache import cache


def client_ip(request):
    """Real client IP. Behind a PaaS proxy REMOTE_ADDR is the proxy, so prefer X-Forwarded-For."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    first = forwarded.split(",")[0].strip()[:64]
    return first or request.META.get("REMOTE_ADDR", "unknown")


def is_blocked(key, limit):
    return cache.get(key, 0) >= limit


def hit(key, window):
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, window)


def clear(key):
    cache.delete(key)
