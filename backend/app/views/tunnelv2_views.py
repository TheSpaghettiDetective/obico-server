import time
import functools
import re
import json
import packaging.version
from types import MethodType
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
import zlib
import sentry_sdk

from lib.view_helpers import get_printer_or_404, get_template_path
from lib import cache
from lib import channels
from lib.tunnelv2 import OctoprintTunnelV2Helper, TunnelAuthenticationError
from app.models import OctoPrintTunnel, calc_normalized_p


import logging
logger = logging.getLogger()


PLUGIN_STATIC_RE = re.compile(r'/plugin/[\w_-]+/static/')
DJANGO_COOKIE_RE = re.compile(
    fr'^{settings.CSRF_COOKIE_NAME}=|'
    fr'^{settings.SESSION_COOKIE_NAME}=|'
    fr'^{settings.LANGUAGE_COOKIE_NAME}='
)

OCTOPRINT_COOKIE_PORT_RE = re.compile(r'^[_\w]+_P(\d+)')

OVER_FREE_LIMIT_HTML = """
<html>
    <body>
        <center>
            <h1>Over Free Limit</h1>
        </center>
        <div>
            <hr>
            <h3 style="color: red;">
                Your month-to-date usage of tunnel data is over
                the free limit. Support this project and get unlimited
                tunnel data by
                <a target="_blank"
                   href="https://app.obico.io/ent_pub/pricing/"
                >upgrading to the Obico app Pro plan</a>,
                or wait for the reset of free limit at the start of
                the next month.
            </h3>
        </div>
    </body>
</html>
"""

MIN_SUPPORTED_VERSION = {
    'octoprint_obico': packaging.version.parse('1.8.4'),
    'moonraker_obico': packaging.version.parse('1.3.0'),
}

NOT_CONNECTED_HTML = """
<html>
    <body>
        <center>
            <h1>Not Connected</h1>
        </center>
        <div>
            <hr>
            <h3 style="color: red;">
                Either your printer is offline,
                or the Obico plugin version is
                lower than the minimum versions:
                <ul>
                    <li>Obico for OctoPrint: 1.8.4</li>
                    <li>Obico Klipper: 1.3.0</li>
                </ul>
            </h3>
        </div>
    </body>
</html>
"""

NOT_CONNECTED_STATUS_CODE = 482
TIMED_OUT_STATUS_CODE = 483
OVER_FREE_LIMIT_STATUS_CODE = 481
NOT_AVAILABLE_STATUS_CODE = 484

def get_agent_name(octoprinttunnel):
    return octoprinttunnel.printer.agent_name or 'octoprint_obico'

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
    tunnel = OctoPrintTunnel.get_or_create_for_internal_use(printer)
    if not tunnel:
        return HttpResponse(f"""
            <html>
                <body>
                    <center>
                        <h3 style="color: red;">Failed to create a new tunnel. Check https://obico.io/docs/server-guides/tunnel/ for details.</h3>
                    </center>
                </body>
            </html>
            """, status=NOT_AVAILABLE_STATUS_CODE)
    url = tunnel.get_internal_tunnel_url(request)
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
    printer = octoprinttunnel.printer
    if request.path.lower() == '/_tsd_/tunnelusage/':
        start_of_next_month = (
            datetime.now().replace(day=1) + timedelta(days=32)
        ).replace(day=1)

        return HttpResponse(
            json.dumps({
                'total': cache.octoprinttunnel_get_stats(printer.user.id),
                'monthly_cap': printer.user.tunnel_cap(),
                'reset_in_seconds': (start_of_next_month - datetime.now()).total_seconds(),
            }),
            content_type='application/json'
        )

    if request.path.lower() == '/_tsd_/webcam/0/':
        pic = (
            cache.printer_pic_get(printer.id) or {}
        ).get('img_url', None)
        return HttpResponse(
            json.dumps({'snapshot': pic}),
            content_type='application/json',
        )

    if request.path.lower() == '/_tsd_/prediction/':
        p = calc_normalized_p(printer.detective_sensitivity, printer.printerprediction)
        return HttpResponse(
            json.dumps({'normalized_p': p}),
            content_type='application/json',
        )

    if request.path.lower() == '/_tsd_/dest_platform_info/': # Currently only Moonraker is supported.
        platform_info = {}
        try:
            platform_info = retrieve_klipper_host_info(octoprinttunnel) # Currently only mobileraker will make this call.
        except:
            sentry_sdk.capture_exception()

        return HttpResponse(
                json.dumps(platform_info),
                content_type='application/json',
            )

    raise Http404


# Helpers


def is_plugin_version_supported(agent: str, version: str) -> bool:
    return packaging.version.parse(version) >= MIN_SUPPORTED_VERSION[agent]


def should_cache(agent, path):
    if agent == 'moonraker_obico':
        return path.startswith('/assets/') or path.startswith('/manifest.webmanifest')
    return path.startswith('/static/') or PLUGIN_STATIC_RE.match(path) is not None


def fix_etag(etag):
    return f'"{etag}"' if etag and '"' not in etag else etag


def fetch_static_etag(request, octoprinttunnel, *args, **kwargs):
    path = request.get_full_path()
    if should_cache(get_agent_name(octoprinttunnel), path):
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
            if should_cache(get_agent_name(octoprinttunnel), path):
                etag = fix_etag(response.get('Etag', ''))
                if etag:
                    cache.octoprinttunnel_update_etag(
                        f'v2.octoprinttunnel_{octoprinttunnel.pk}',
                        path,
                        etag
                    )

        return response
    return inner


def set_response_items(self: HttpResponse):
    items = list(self.headers.items())
    if hasattr(self, "tunnel_cookies"):
        for raw_cookie in self.tunnel_cookies:
            items.append(('Set-Cookie', raw_cookie))
    return items


def retrieve_klipper_host_info(octoprinttunnel):
    resp = _tunnel_http_req_and_wait_for_resp(octoprinttunnel,  "/machine/system_info", "get", {}, b'')
    network_dict = json.loads(resp.content.decode('utf-8')).get('result', {}).get('system_info', {}).get('network', {})
    ip_addrs = [
        ip['address'] for wlan in network_dict.values()
        for ip in wlan['ip_addresses'] if not ip['is_link_local'] and ip['family'] == 'ipv4' # is_link_local is true for 127.0.0.1
    ]
    ip_addrs +=[
        ip['address'] for wlan in network_dict.values()
        for ip in wlan['ip_addresses'] if not ip['is_link_local'] and ip['family'] == 'ipv6'
    ]
    if len(ip_addrs) == 0:
        return {}

    ip_addr = ip_addrs[0]
    resp = _tunnel_http_req_and_wait_for_resp(octoprinttunnel,  "/server/config", "get", {}, b'')
    server_port = json.loads(resp.content.decode('utf-8')).get('result', {}).get('config', {}).get('server', {}).get('port')

    return {'server_ip': ip_addr, 'server_port': server_port, 'linked_name': octoprinttunnel.printer.name}

@save_static_etag
@condition(etag_func=fetch_static_etag)
def _octoprint_http_tunnel(request, octoprinttunnel):
    user = octoprinttunnel.printer.user
    version = octoprinttunnel.printer.agent_version or '0.0'

    if user.tunnel_usage_over_cap():
        return HttpResponse(
            OVER_FREE_LIMIT_HTML,
            status=OVER_FREE_LIMIT_STATUS_CODE)

    # if plugin is disconnected, halt
    if channels.num_ws_connections(channels.octo_group_name(octoprinttunnel.printer.id)) < 1:
        return HttpResponse(
            NOT_CONNECTED_HTML,
            status=NOT_CONNECTED_STATUS_CODE)

    if not is_plugin_version_supported(get_agent_name(octoprinttunnel), version):
        return HttpResponse(
            NOT_CONNECTED_HTML,
            status=NOT_CONNECTED_STATUS_CODE)

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

    if 'content-type' in request.headers:
        req_headers['Content-Type'] = request.headers['content-type']

    if 'cookie' in request.headers:
        # let's not forward cookies of TSD server
        stripped_cookies = '; '.join(
            [
                cookie.strip()
                for cookie in request.headers['cookie'].split(';')
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
                for h in request.headers['authorization'].split(',')
                if h != request.auth_header
            ]
        )
        if stripped_auth_heaader:
            req_headers['Authorization'] = stripped_auth_heaader

    return _tunnel_http_req_and_wait_for_resp(octoprinttunnel, path, method, req_headers, request.body, request_is_secure=request.is_secure())


def _tunnel_http_req_and_wait_for_resp(octoprinttunnel, path, method, req_headers, request_body, request_is_secure=False):
    user = octoprinttunnel.printer.user
    ref = f'v2.{octoprinttunnel.id}.{method}.{time.time()}.{path}'

    msg = (
        octoprinttunnel.printer.id,
        {
            'http.tunnelv2': {
                'ref': ref,
                'method': method,
                'headers': req_headers,
                'path': path,
                'data': request_body
            },
            'as_binary': True,
        }
    )
    channels.send_msg_to_printer(*msg)

    data = cache.octoprinttunnel_http_response_get(ref)
    if data is None:
        # request timed out
        return HttpResponse(
            NOT_CONNECTED_HTML,
            status=TIMED_OUT_STATUS_CODE)

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
        'set-cookie',
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
    tunnel_cookies = []
    for cookie in (data['response'].get('cookies', ()) or ()):
        if (
            request_is_secure and
            'secure' not in cookie.lower()
        ):
            cookie += '; Secure'

        if 'Expires=' not in cookie and 'Max-Age=' not in cookie:
            cookie += '; Max-Age=7776000'  # 3 months

        m = OCTOPRINT_COOKIE_PORT_RE.match(cookie)
        if m is not None:
            # OctoPrint JS needs the port in csrf_token_P{port} to be the one in browser. But the backend returns the port that plugins connects to.
            # Hence we need to do this dance to duplicate the cookies between them.
            # https://github.com/OctoPrint/OctoPrint/commit/59a0c8e8d79e9d28c4a2dfbf4105f8dd580a8f04
            cookie_port = octoprinttunnel.port
            if not cookie_port:
                cookie_port = 443 if request_is_secure else 80
            tunnel_cookies.append(cookie.replace(f"P{m.groups()[0]}", f"P{cookie_port}"))

        tunnel_cookies.append(cookie)

    if tunnel_cookies:
        setattr(resp, 'tunnel_cookies', tunnel_cookies)
        # Unfortunately Django 2 still doesn't have a good way to set headers and hence we have to do this ugly trick
        resp.items = MethodType(set_response_items, resp)

    if data['response'].get('compressed', False):
        content = zlib.decompress(data['response']['content'])
    else:
        content = data['response']['content']

    cache.octoprinttunnel_update_stats(user.id, len(content))

    if get_agent_name(octoprinttunnel) == 'moonraker_obico' and path == ('/') and isinstance(content, bytes):
        # manifest file is fetched without cookie by default, forcing cookie here. https://stackoverflow.com/a/57184506
        content = content.replace(
            b'href="/manifest.webmanifest"',
            b'href="/manifest.webmanifest" crossorigin="use-credentials"'
        )

    resp.write(content)
    return resp
