import time
import functools
import re
import json
import packaging.version
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
from django.core.exceptions import PermissionDenied
import zlib

from lib.view_helpers import get_printer_or_404, get_template_path, get_printers
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
                   href="https://app.thespaghettidetective.com/ent/pricing/"
                >upgrading to The Spaghetti Detective Pro plan</a>,
                or wait for the reset of free limit at the start of
                the next month.
            </h3>
        </center>
    </body>
</html>
"""

NOT_CONNECTED_HTML = """
<html>
    <body>
        <center>
            <h1>Not Connected</h1>
            <hr>
            <h3 style="color: red;">
                Either your OctoPrint is offline,
                or The Spaghetti Detective plugin version is
                lower than 1.4.0.
            </h3>
        </center>
    </body>
</html>
"""

NOT_CONNECTED_STATUS_CODE = 482
TIMED_OUT_STATUS_CODE = 483
OVER_FREE_LIMIT_STATUS_CODE = 481

MIN_SUPPORTED_VERSION = packaging.version.parse('1.8.4')


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

    if request.path.lower().startswith('/_tsd_/'): # "Special path" starting with "/_tsd_/" is dedicated to tunnel APIs
        return tunnel_api(request, octoprinttunnel)

    return _octoprint_http_tunnel(request, octoprinttunnel)


def tunnel_api(request, octoprinttunnel):
    if request.path.lower() == '/_tsd_/tunnelusage/':
        start_of_next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)

        return HttpResponse(
            json.dumps({
                'total': cache.octoprinttunnel_get_stats(octoprinttunnel.printer.user.id),
                'monthly_cap': -1 if octoprinttunnel.printer.user.is_pro else settings.OCTOPRINT_TUNNEL_CAP,
                'reset_in_seconds': (start_of_next_month - datetime.now()).total_seconds(),
            }),
            content_type='application/json'
        )

    if request.path.lower() == '/_tsd_/webcam/0/':
        pic = (cache.printer_pic_get(octoprinttunnel.printer.id) or {}).get('img_url', None)
        return HttpResponse(
            json.dumps({'snapshot': pic}),
            content_type='application/json',
        )

    raise Http404

# Helpers


def is_plugin_version_supported(version: str) -> bool:
    return packaging.version.parse(version) >= MIN_SUPPORTED_VERSION


def should_cache(path):
    return path.startswith('/static/') or PLUGIN_STATIC_RE.match(path)


def fix_etag(etag):
    return f'"{etag}"' if etag and '"' not in etag else etag


def fetch_static_etag(request, octoprinttunnel, *args, **kwargs):
    path = request.get_full_path()

    if should_cache(path):
        cached_etag = cache.octoprinttunnel_get_etag(
            f'octoprinttunnel_{octoprinttunnel.pk}', path)
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
                        f'octoprinttunnel_{octoprinttunnel.pk}',
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

    if channels.num_ws_connections(channels.octo_group_name(octoprinttunnel.printer.id)) < 1:
        return HttpResponse(NOT_CONNECTED_HTML, status=NOT_CONNECTED_STATUS_CODE)

    method = request.method.lower()
    path = request.get_full_path()

    IGNORE_HEADERS = [
        'HTTP_HOST', 'HTTP_ORIGIN', 'HTTP_REFERER', 'HTTP_AUTHORIZATION',
        'HTTP_COOKIE', 'HTTP_ACCEPT_ENCODING',
    ]

    req_headers = {
        k[5:].replace('_', ' ').title().replace(' ', '-'): v
        for (k, v) in request.META.items()
        if (
            k.startswith('HTTP') and
            k not in IGNORE_HEADERS and
            not k.startswith('HTTP_X_FORWARDED')
        )
    }

    if 'CONTENT_TYPE' in request.META:
        req_headers['Content-Type'] = request.META['CONTENT_TYPE']

    if 'HTTP_COOKIE' in request.META:
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
        stripped_auth_heaader = ', '.join(
            [
                h
                for h in request.META['HTTP_AUTHORIZATION'].split(',')
                if h != request.auth_header
            ]
        )
        if stripped_auth_heaader:
            req_headers['Authorization'] = stripped_auth_heaader

    ref = f'{octoprinttunnel.id}.{method}.{time.time()}.{path}'

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
        return HttpResponse(NOT_CONNECTED_HTML, status=TIMED_OUT_STATUS_CODE)

    content_type = data['response']['headers'].get('Content-Type') or None
    status_code = data['response']['status']

    resp = HttpResponse(
        status=status_code,
        content_type=content_type,
    )

    to_ignore = ('content-length', 'content-encoding', 'x-frame-options')
    for k, v in data['response']['headers'].items():
        if k.lower() in to_ignore:
            continue

        if k.lower() == 'etag':
            v = fix_etag(v)

        resp[k] = v

    for cookie in (data['response'].get('cookies', ()) or ()):
        if (
            request.is_secure() and
            'secure' not in cookie.lower()
        ):
            cookie += '; Secure'

        resp['Set-Cookie'] = cookie

    if data['response'].get('compressed', False):
        content = zlib.decompress(data['response']['content'])
    else:
        content = data['response']['content']

    cache.octoprinttunnel_update_stats(
        user.id,
        # x1.2 because sent data volume is 20% of received.
        # x2 because all data need to go in and out. 240 bytes header overhead
        (len(content) + 240) * 1.2 * 2
    )

    resp.write(content)
    return resp
