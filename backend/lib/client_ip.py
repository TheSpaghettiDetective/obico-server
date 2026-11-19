from rest_framework.throttling import BaseThrottle


def client_ip(request):
    """The client's address as DRF's throttles see it: X-Forwarded-For counted
    back NUM_TRUSTED_PROXIES entries, or the connection's address when it is 0."""
    return BaseThrottle().get_ident(request)
