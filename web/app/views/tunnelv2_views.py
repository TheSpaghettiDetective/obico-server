import time
import functools
import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition

import zlib

from lib.view_helpers import get_printer_or_404, get_template_path
from lib import cache
from lib import channels

import logging
logger = logging.getLogger()

PLUGIN_STATIC_RE = re.compile(r'/plugin/[\w_-]+/static/')

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

TIMED_OUT_HTML = """
<html>
    <body>
        <center>
            <h1>Timed Out</h1>
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


def should_cache(path):
    return path.startswith('/static/') or PLUGIN_STATIC_RE.match(path)


def fix_etag(etag):
    return f'"{etag}"' if etag and '"' not in etag else etag


@login_required
def tunnel(request, pk, template_dir=None):
    return render(request, get_template_path('tunnel', template_dir))


def fetch_static_etag(request, pk, *args, **kwargs):
    path = request.get_full_path()

    if should_cache(path):
        cached_etag = cache.octoprinttunnel_get_etag(pk, path)
        if cached_etag:
            return cached_etag

    return None


def save_static_etag(func):
    @functools.wraps(func)
    def inner(request, pk, *args, **kwargs):
        response = func(request, pk, *args, **kwargs)

        if response.status_code in (200, 304):
            path = request.get_full_path()

            if should_cache(path):
                etag = fix_etag(response.get('Etag', ''))
                if etag:
                    cache.octoprinttunnel_update_etag(pk, path, etag)

        return response
    return inner


@csrf_exempt
@save_static_etag
@condition(etag_func=fetch_static_etag)
def octoprint_http_tunnel(request, pk):
    if not request.user.is_authenticated:
        # need a way to redirect to main login
        return HttpResponse(
            'unauthenticated',
            status=401,
        )

    get_printer_or_404(pk, request)

    if request.user.tunnel_usage_over_cap():
        return HttpResponse(
            OVER_FREE_LIMIT_HTML,
            status=412)

    method = request.method.lower()
    path = request.get_full_path()

    IGNORE_HEADERS = [
        'HTTP_HOST', 'HTTP_ORIGIN', 'HTTP_REFERER',
    ]

    # Recreate http headers, because django put headers
    # in request.META as "HTTP_XXX_XXX". Is there a better way?
    req_headers = {
        k[5:].replace("_", " ").title().replace(" ", "-"): v
        for (k, v) in request.META.items()
        if (
            k.startswith("HTTP") and
            not k.startswith('HTTP_X_') and
            k not in IGNORE_HEADERS
        )
    }

    if 'CONTENT_TYPE' in request.META:
        req_headers['Content-Type'] = request.META['CONTENT_TYPE']

    ref = f'{pk}.{method}.{time.time()}.{path}'

    channels.send_msg_to_printer(
        pk,
        {
            "http.tunnelv2": {
                "ref": ref,
                "method": method,
                "headers": req_headers,
                "path": path,
                "data": request.body
            },
            'as_binary': True,
        })

    data = cache.octoprinttunnel_http_response_get(ref)
    if data is None:
        return HttpResponse(
            TIMED_OUT_HTML,
            status=504)

    content_type = data['response']['headers'].get('Content-Type') or None
    resp = HttpResponse(
        status=data["response"]["status"],
        content_type=content_type,
    )
    for k, v in data['response']['headers'].items():
        if k in ['Content-Length', 'Content-Encoding']:
            continue

        if k == 'Etag':
            v = fix_etag(v)

        resp[k] = v

    for cookie in (data['response']['cookies'] or ()):
        resp['Set-Cookie'] = cookie

    if data['response'].get('compressed', False):
        content = zlib.decompress(data['response']['content'])
    else:
        content = data['response']['content']

    cache.octoprinttunnel_update_stats(
        request.user.id,
        # x1.2 because sent data volume is 20% of received.
        # x2 because all data need to go in and out. 240 bytes header overhead
        (len(content) + 240) * 1.2 * 2
    )

    resp.write(content)
    return resp
