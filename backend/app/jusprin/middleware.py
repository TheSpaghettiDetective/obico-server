from app.jusprin.language_utils import activate_language_from_param


def jusprin_lang_middleware(get_response):
    """
    Middleware to activate Django translations based on ?lang= query parameter
    for JusPrin API requests (/jusprin/api/...).

    Maps IETF language tags (e.g., zh-CN, pt-BR) to Django language codes.
    This middleware runs after LocaleMiddleware to override its language selection
    when ?lang= parameter is present.
    """
    def middleware(request):
        # Only process JusPrin API requests
        if request.path.startswith('/jusprin/api/'):
            lang_param = request.GET.get('lang')
            if lang_param:
                django_lang = activate_language_from_param(lang_param)
                if django_lang:
                    request.LANGUAGE_CODE = django_lang

        response = get_response(request)
        return response

    return middleware

