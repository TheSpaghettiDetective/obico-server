import time
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .view_helpers import get_printer_or_404
from lib import redis
from lib import channels


@login_required
def tunnel(request, printer_id):
    return render(request, 'tunnel.html', {'printer': get_printer_or_404(printer_id, request)})

@csrf_exempt
@login_required
def octoprint_http_tunnel(request, printer_id):
    get_printer_or_404(printer_id, request)

    prefix = f'/octoprint/{printer_id}'  # FIXME
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
            }
        },
        as_binary=True)

    data = redis.octoprinttunnel_http_response_get(ref)
    if data is None:
        return HttpResponse('Timed out. Either your OctoPrint is offline, or The Spaghetti Detective plugin version is lower than 1.4.0.')

    content_type = data['response']['headers'].get('Content-Type') or None
    resp = HttpResponse(
        status=data["response"]["status"],
        content_type=content_type,
    )
    for k, v in data['response']['headers'].items():
        if k == 'Content-Length':
            continue
        resp[k] = v

    content = data['response']['content']
    if content_type and content_type.startswith('text/html'):
        content = rewrite_html(prefix, ensure_bytes(content))
    elif path.endswith('app/client/socket.js'):
        content = rewrite_socket_js(ensure_bytes(content))
    elif path.endswith('sockjs.js'):
        content = rewrite_sockjs_js(ensure_bytes(content))
    elif path.endswith('sockjs.min.js'):
        content = rewrite_sockjs_min_js(ensure_bytes(content))
    elif path.endswith('loginui/static/js/main.js'):
        content = rewrite_loginui_main_js(prefix, ensure_bytes(content))

    resp.write(content)

    return resp


def ensure_bytes(content):
    # If plugin side runs on py2.7
    # then content is potentially a string.
    # Rewriting later expects bytes.
    if not isinstance(content, bytes):
        return content.encode()
    return content


def rewrite_socket_js(content):
    # force websocket-only connection
    # xhr(-streams/etc) won't work for now
    return content.replace(
        b'OctoPrintSocketClient.prototype.connect = function(opts) {',
        b'OctoPrintSocketClient.prototype.connect = function(opts) {\nopts = opts || {}; opts["transports"] = ["websocket", ];\n'  # noqa
    )


def rewrite_sockjs_js(content):
    # Route sockjs to "^/ws/" as Ops requires all websocket path starts with "/ws"
    return content.replace(
        b"urlUtils.addPath(transUrl, '/websocket')",
        b"urlUtils.addPath(transUrl.replace('/octoprint', '/ws/octoprint'), '/websocket')"
    )


def rewrite_sockjs_min_js(content):
    # Route sockjs to "^/ws/" as Ops requires all websocket path starts with "/ws"
    return content.replace(
        b'addPath(t,"/websocket")',
        b'addPath(t.replace("/octoprint", "/ws/octoprint"),"/websocket")'
    )


def rewrite_loginui_main_js(prefix, content):
    return content.replace(
        b'BASE_URL;',
        f'"{prefix}" + BASE_URL;'.encode()
    )


def rewrite_html(prefix, content):
    # rewirte urls
    return content\
        .replace(b'src="/',
                 f'src="{prefix}/'.encode())\
        .replace(b'href="/',
                 f'href="{prefix}/'.encode())\
        .replace(b'var BASEURL = "/',
                 f'var BASEURL = "{prefix}'.encode())\
        .replace(b'var GCODE_WORKER = "/',
                 f'var GCODE_WORKER = "{prefix}'.encode())
