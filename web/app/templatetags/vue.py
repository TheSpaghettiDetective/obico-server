from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from webpack_loader.templatetags.webpack_loader import render_bundle

register = template.Library()

STATIC_BUNDLE_PREFIX = settings.STATIC_BUNDLE_PREFIX
TEMPLATES = {
    'js': '<script type="text/javascript" src="{0}" {1}></script>',
    'css': '<link type="text/css" href="{0}" rel="stylesheet" {1}/>'
}


@register.simple_tag
def bundle(bundle_name, extension=None, config='DEFAULT', attrs=''):
    if settings.WEBPACK_LOADER_ENABLED:
        return render_bundle(
            bundle_name, extension=extension, config=config, attrs=attrs)
    else:
        tags = []
        extensions = (extension, ) if extension is not None else ('js', 'css')

        for ext in extensions:
            url = static(f'{STATIC_BUNDLE_PREFIX}/{ext}/{bundle_name}.{ext}')

            t = TEMPLATES.get(ext)

            if t is not None:
                tags.append(t.format(url, attrs))

        return mark_safe("\n".join(tags))
