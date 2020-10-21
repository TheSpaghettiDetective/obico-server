import time
import functools
import urllib.parse
import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.conf import settings

from .view_helpers import get_printer_or_404
from lib import cache
from lib import channels

import logging
logger = logging.getLogger()


@login_required
def tunnel(request, printer_id):
    printer = get_printer_or_404(printer_id, request)
    return render(request, 'tunnel.html', {'printer': printer})


@csrf_exempt
@login_required
def octoprint_http_tunnel(request, printer_id):
    get_printer_or_404(printer_id, request)
    if request.user.tunnel_usage_over_cap():
        return HttpResponse('<html><body><center><h1>Over Free Limit</h1><hr><h3 style="color: red;">Your month-to-date usage of OctoPrint Tunneling is over the free limit. Upgrade to The Spaghetti Detective Pro plan for unlimited tunneling, or wait for the reset of free limit at the start of the next month.</h3></center></body></html>', status=412)

    prefix = f'/octoprint/{printer_id}'
    method = request.method.lower()
    path = request.get_full_path()[len(prefix):]

    IGNORE_HEADERS = [
        'HTTP_HOST', 'HTTP_ORIGIN', 'HTTP_REFERER', 'HTTP_COOKIE',
    ]

    # Recreate http headers, because django put headers in request.META as "HTTP_XXX_XXX". Is there a better way?
    req_headers = {
        k[5:].replace("_", " ").title().replace(" ", "-"): v
        for (k, v) in request.META.items()
        if k.startswith("HTTP") and not k.startswith('HTTP_X_') and k not in IGNORE_HEADERS
    }

    if 'CONTENT_TYPE' in request.META:
        req_headers['Content-Type'] = request.META['CONTENT_TYPE']

    ref = f'{printer_id}.{method}.{time.time()}.{path}'

    channels.send_msg_to_printer(
        printer_id,
        {
            "http.tunnel": {
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
        return HttpResponse('<html><body><center><h1>Timed Out</h1><hr><h3 style="color: red;">Either your OctoPrint is offline, or The Spaghetti Detective plugin version is lower than 1.4.0.</h3></center></body></html>', status=504)

    content_type = data['response']['headers'].get('Content-Type') or None
    resp = HttpResponse(
        status=data["response"]["status"],
        content_type=content_type,
    )
    for k, v in data['response']['headers'].items():
        if k in ['Content-Length', 'Content-Encoding']:
            continue
        resp[k] = v

    url_path = urllib.parse.urlparse(path).path
    content = data['response']['content']

    cache.octoprinttunnel_update_stats(
        request.user.id,
        (len(content)+ 240) * 1.2 * 2  # x1.2 because sent data volume is 20% of received. x2 because all data need to go in and out. 240 bytes header overhead
    )

    if content_type and content_type.startswith('text/html'):
        content = rewrite_html(prefix, ensure_bytes(content))
    elif url_path.endswith('jquery.js') or url_path.endswith('jquery.min.js'):
        content = inject_ajax_prefilter(prefix, content)
    elif url_path.endswith('socket.js'):
        content = re.sub(_R_SOCKJS_TRANSPORTS,
                         _rewrite_sockjs_transports, ensure_bytes(content))
    elif url_path.endswith('packed_client.js'):
        content = re.sub(_R_SOCKJS_TRANSPORTS,
                         _rewrite_sockjs_transports, ensure_bytes(content))
    elif url_path.endswith('packed_libs.js'):
        content = re.sub(_R_WS_CONNECT_PATH,
                         _rewrite_ws_connect_path, ensure_bytes(content))
        content = inject_ajax_prefilter(prefix, content)
    elif url_path.endswith('sockjs.js'):
        content = re.sub(_R_WS_CONNECT_PATH,
                         _rewrite_ws_connect_path, ensure_bytes(content))
    elif url_path.endswith('sockjs.min.js'):
        content = re.sub(_R_WS_CONNECT_PATH,
                         _rewrite_ws_connect_path, ensure_bytes(content))

    resp.write(content)

    return resp


def ensure_bytes(content):
    # If plugin side runs on py2.7
    # then content is potentially a string.
    # Rewriting later expects bytes.
    if not isinstance(content, bytes):
        return content.encode()
    return content


def rewrite_html(prefix, content):
    content = re.sub(
        _R_SRC_IN_QUOTES,
        functools.partial(_rewrite_url, b'src', prefix.encode()),
        content)
    content = re.sub(
        _R_HREF_IN_QUOTES,
        functools.partial(_rewrite_url, b'href', prefix.encode()),
        content)

    return content\
        .replace(b'var BASEURL = "/',
                 f'var BASEURL = "{prefix}/'.encode())\
        .replace(b'var BASE_URL = "/',
                 f'var BASE_URL = "{prefix}/'.encode())\
        .replace(b'var GCODE_WORKER = "/',
                 f'var GCODE_WORKER = "{prefix}/'.encode())


_R_WS_CONNECT_PATH = re.compile(b'addPath\\((\\w+), *./websocket.\\)')


def _rewrite_ws_connect_path(match):
    # websocket worker pool in production is configured for /ws only
    g = match.group(1)
    b = b'%b.replace("/octoprint", "/ws/octoprint")' % g
    return b'addPath(%b, "/websocket")' % b


_R_SOCKJS_TRANSPORTS = re.compile(
    b'OctoPrintSocketClient.prototype.connect *= *function\\(opts\\) *{')


def _rewrite_sockjs_transports(match):
    # force websocket-only connection
    # xhr(-streams/etc) won't work for now
    return b'OctoPrintSocketClient.prototype.connect=function(opts){opts=opts||{};opts["transports"]=["websocket",];'  # noqa


_R_SRC_IN_QUOTES = re.compile(b'src=[\'"](.*?)[\'"]')
_R_HREF_IN_QUOTES = re.compile(b'href=[\'"](.*?)[\'"]')


def _rewrite_url(attr, prefix, match):
    url = match.groups()[0]

    if not url.startswith(b'#') and not url.startswith(b'javascript:'):
        # logger.info(b'%b %b' % (attr, url))

        parts = urllib.parse.urlsplit(url)
        if parts.netloc == b'':
            new_path = (prefix + b"/" + parts.path).replace(b"//", b"/")
            parts = parts._replace(path=new_path)

            url = urllib.parse.urlunsplit(parts)
    return b'%s="%b"' % (attr, url)


def inject_ajax_prefilter(prefix, content):
    # Plugins have different ajax url building startegies.
    # Sometimes our modified BASEURL breaks them.
    # Let's clean them up by removing&readding our prefix.
    # Slashes need some extra care, in some cases they are missing
    # at unexpected places and we try to fix those here too.
    code = b'''\n
    (function($) {
      $.ajaxPrefilter(function(options) {
        var url = options.url;

        var url = url.replace("%b", "/");
        url = url.replace("//", "/");
        if (!url.startsWith('http') && !url.startsWith("/")) {
            url = "/" + url;
        }
        url = "%b" + url;

        if (options.url != url) {
          console.log("[TSD] url is rewritten", {from: options.url, to: url});
        }

        options.url = url;
      })
    }(jQuery))''' % (prefix.encode(), prefix.encode())
    if not isinstance(content, (bytes, bytearray)):
        code = code.decode()
    content += code
    return content
