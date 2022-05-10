import time
import functools
import re
import json
import packaging.version
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
import zlib

from lib.view_helpers import get_printer_or_404, get_template_path
from lib import cache
from lib import channels
from lib.tunnelv2 import OctoprintTunnelV2Helper, TunnelAuthenticationError
from app.models import OctoPrintTunnel


import logging
logger = logging.getLogger()


PLUGIN_STATIC_RE = re.compile(r'/plugin/[\w_-]+/static/')
DJANGO_COOKIE_RE = re.compile(
    fr'^{settings.CSRF_COOKIE_NAME}=|'
    fr'^{settings.SESSION_COOKIE_NAME}=|'
    fr'^{settings.LANGUAGE_COOKIE_NAME}='
)


OVER_FREE_LIMIT_HTML = """
<html>
    <body>
        <center>
            <h1>Over Free Limit</h1>
            <hr>
            <h3 style="color: red;">
                Your month-to-date usage of OctoPrint Tunneling is over
                the free limit. Support this project and get unlimited
                tunneling by
                <a target="_blank"
                   href="https://app.obico.io/ent_pub/pricing/"
                >upgrading to the Obico app Pro plan</a>,
                or wait for the reset of free limit at the start of
                the next month.
            </h3>
        </center>
    </body>
</html>
"""

MIN_SUPPORTED_VERSION = packaging.version.parse('1.8.4')

NOT_CONNECTED_HTML = f"""
<html>
    <body>
        <center>
            <h1>Not Connected</h1>
            <hr>
            <h3 style="color: red;">
                Either your OctoPrint is offline,
                or the Obico plugin version is
                lower than {MIN_SUPPORTED_VERSION.public}.
            </h3>
        </center>
    </body>
</html>
"""

NOT_CONNECTED_STATUS_CODE = 482
TIMED_OUT_STATUS_CODE = 483
OVER_FREE_LIMIT_STATUS_CODE = 481


def sanitize_app_name(app_name: str) -> str:
    return app_name.strip()[:64]


def new_octoprinttunnel(request):
    return render(request, 'new_octoprinttunnel.html')


@login_required
def new_octoprinttunnel_succeeded(request):
    return render(request, 'new_octoprinttunnel_succeeded.html')


@login_required
def tunnel(request, pk, template_dir=None):
    get_printer_or_404(pk, request)
    return render(
        request,
        get_template_path('tunnel', template_dir),
    )


@csrf_exempt
@login_required
def redirect_to_tunnel_url(request, pk):
    printer = get_printer_or_404(pk, request)
    pt = OctoPrintTunnel.get_or_create_for_internal_use(printer)
    url = pt.get_internal_tunnel_url(request)
    return HttpResponseRedirect(url)


@csrf_exempt
@xframe_options_exempt
def octoprint_http_tunnel(request):
    try:
        octoprinttunnel = OctoprintTunnelV2Helper.get_octoprinttunnel(request)
    except TunnelAuthenticationError as exc:
        resp = HttpResponse(
            exc.message,
            status=401
        )
        if exc.realm:
            resp['WWW-Authenticate'] =\
                f'Basic realm="{exc.realm}", charset="UTF-8"'
        return resp

    # "Special path" starting with "/_tsd_/" is dedicated to tunnel APIs
    if request.path.lower().startswith('/_tsd_/'):
        return tunnel_api(request, octoprinttunnel)

    resp = _octoprint_http_tunnel(request, octoprinttunnel)
    setattr(resp, '_from_tunnelv2', True)
    return resp


def tunnel_api(request, octoprinttunnel):
    if request.path.lower() == '/_tsd_/tunnelusage/':
        start_of_next_month = (
            datetime.now().replace(day=1) + timedelta(days=32)
        ).replace(day=1)

        return HttpResponse(
            json.dumps({
                'total': cache.octoprinttunnel_get_stats(octoprinttunnel.printer.user.id),
                'monthly_cap': octoprinttunnel.printer.user.tunnel_cap(),
                'reset_in_seconds': (start_of_next_month - datetime.now()).total_seconds(),
            }),
            content_type='application/json'
        )

    if request.path.lower() == '/_tsd_/webcam/0/':
        pic = (
            cache.printer_pic_get(octoprinttunnel.printer.id) or {}
        ).get('img_url', None)
        return HttpResponse(
            json.dumps({'snapshot': pic}),
            content_type='application/json',
        )

    raise Http404

# Helpers


def is_plugin_version_supported(version: str) -> bool:
    return packaging.version.parse(version) >= MIN_SUPPORTED_VERSION


def should_cache(path):
    return path.startswith('/static/') or PLUGIN_STATIC_RE.match(path) is not None


def fix_etag(etag):
    return f'"{etag}"' if etag and '"' not in etag else etag


def fetch_static_etag(request, octoprinttunnel, *args, **kwargs):
    path = request.get_full_path()

    if should_cache(path):
        cached_etag = cache.octoprinttunnel_get_etag(
            f'v2.octoprinttunnel_{octoprinttunnel.pk}', path)
        if cached_etag:
            return cached_etag

    return None


def save_static_etag(func):
    @functools.wraps(func)
    def inner(request, octoprinttunnel, *args, **kwargs):
        response = func(request, octoprinttunnel, *args, **kwargs)

        if response.status_code in (200, 304):
            path = request.get_full_path()

            if should_cache(path):
                etag = fix_etag(response.get('Etag', ''))
                if etag:
                    cache.octoprinttunnel_update_etag(
                        f'v2.octoprinttunnel_{octoprinttunnel.pk}',
                        path,
                        etag
                    )

        return response
    return inner


@save_static_etag
@condition(etag_func=fetch_static_etag)
def _octoprint_http_tunnel(request, octoprinttunnel):
    user = octoprinttunnel.printer.user
    if user.tunnel_usage_over_cap():
        return HttpResponse(OVER_FREE_LIMIT_HTML, status=OVER_FREE_LIMIT_STATUS_CODE)

    # if plugin is disconnected, halt
    if channels.num_ws_connections(channels.octo_group_name(octoprinttunnel.printer.id)) < 1:
        return HttpResponse(NOT_CONNECTED_HTML, status=NOT_CONNECTED_STATUS_CODE)

    version = (
        cache.printer_settings_get(octoprinttunnel.printer.pk) or {}
    ).get('tsd_plugin_version', '')
    is_v1 = version and not is_plugin_version_supported(version)
    if is_v1:
        return HttpResponse(NOT_CONNECTED_HTML, status=NOT_CONNECTED_STATUS_CODE)

    method = request.method.lower()
    path = request.get_full_path()

    IGNORE_HEADERS = [
        'HTTP_HOST', 'HTTP_ORIGIN', 'HTTP_REFERER',  # better not to tell
        'HTTP_AUTHORIZATION',  # handled explicitely
        'HTTP_COOKIE',  # handled explicitely
        'HTTP_ACCEPT_ENCODING',  # should be handled by TSD server
    ]

    req_headers = {
        k[5:].replace('_', ' ').title().replace(' ', '-'): v
        for (k, v) in request.META.items()
        if (
            k.startswith('HTTP') and
            k not in IGNORE_HEADERS and
            not k.startswith('HTTP_X_FORWARDED')  # meant for TSD server
        )
    }

    if 'CONTENT_TYPE' in request.META:
        req_headers['Content-Type'] = request.META['CONTENT_TYPE']

    if 'HTTP_COOKIE' in request.META:
        # let's not forward cookies of TSD server
        stripped_cookies = '; '.join(
            [
                cookie.strip()
                for cookie in request.META['HTTP_COOKIE'].split(';')
                if DJANGO_COOKIE_RE.match(cookie.strip()) is None
            ]
        )
        if stripped_cookies:
            req_headers['Cookie'] = stripped_cookies

    if hasattr(request, 'auth_header'):
        # let's not forward basic auth header of external tunnel
        stripped_auth_heaader = ', '.join(
            [
                h
                for h in request.META['HTTP_AUTHORIZATION'].split(',')
                if h != request.auth_header
            ]
        )
        if stripped_auth_heaader:
            req_headers['Authorization'] = stripped_auth_heaader

    ref = f'v2.{octoprinttunnel.id}.{method}.{time.time()}.{path}'

    channels.send_msg_to_printer(
        octoprinttunnel.printer.id,
        {
            'http.tunnelv2': {
                'ref': ref,
                'method': method,
                'headers': req_headers,
                'path': path,
                'data': request.body
            },
            'as_binary': True,
        })

    data = cache.octoprinttunnel_http_response_get(ref)
    if data is None:
        # request timed out
        return HttpResponse(NOT_CONNECTED_HTML, status=TIMED_OUT_STATUS_CODE)

    content_type = data['response']['headers'].get('Content-Type') or None
    status_code = data['response']['status']

    resp = HttpResponse(
        status=status_code,
        content_type=content_type,
    )

    to_ignore = (
        'content-length',  # set by django
        'content-encoding',  # if its set, it is probably incorrect/unapplicable
        'x-frame-options',  # response must load in TSD's iframe
    )
    for k, v in data['response']['headers'].items():
        if k.lower() in to_ignore:
            continue

        if k.lower() == 'etag':
            # pre 1.6.? octoprint has invalid etag format for some responses
            v = fix_etag(v)

        resp[k] = v

    # plugin connects over http to octoprint,
    # but TSD needs cookies working over https.
    # without this, cookies set in response might not be used
    # in some browsers (FF gives wwarning)
    for cookie in (data['response'].get('cookies', ()) or ()):
        if (
            request.is_secure() and
            'secure' not in cookie.lower()
        ):
            cookie += '; Secure'

        if 'Expires=' not in cookie and 'Max-Age=' not in cookie:
            cookie += '; Max-Age=7776000'  # 3 months

        resp['Set-Cookie'] = cookie

    if data['response'].get('compressed', False):
        content = zlib.decompress(data['response']['content'])
    else:
        content = data['response']['content']

    cache.octoprinttunnel_update_stats(user.id, len(content))

    resp.write(content)
    return resp
