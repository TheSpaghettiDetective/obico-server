from django.utils import translation
from django.conf import settings


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
                # Normalize: replace underscores with hyphens and lowercase
                lang_normalized = lang_param.replace('_', '-').lower()

                # Map IETF tags to Django language codes
                # Django uses lowercase with hyphens (e.g., 'zh-cn', 'pt-br')
                lang_mapping = {
                    'zh-cn': 'zh-cn',
                    'zh-tw': 'zh-tw',
                    'pt-br': 'pt-br',
                    'en-us': 'en',
                    'en': 'en',
                    'es': 'es',
                    'de': 'de',
                    'fr': 'fr',
                    'it': 'it',
                    'ru': 'ru',
                }

                # Get Django language code from mapping, or try to find supported variant
                django_lang = lang_mapping.get(lang_normalized)
                if not django_lang:
                    # Try to get supported language variant
                    try:
                        django_lang = translation.get_supported_language_variant(lang_normalized)
                    except LookupError:
                        # Fallback to default language if not supported
                        django_lang = settings.LANGUAGE_CODE.split('-')[0]

                # Activate the language for this request
                translation.activate(django_lang)
                request.LANGUAGE_CODE = django_lang

        response = get_response(request)
        return response

    return middleware

