import sys
import time
from unittest import mock

import pytest
import requests
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

# Stub the model loader so importing server.py doesn't require darknet weights
sys.modules.setdefault('lib.detection_model', mock.MagicMock())

import server  # noqa: E402


@pytest.fixture(autouse=True)
def no_backoff_sleep():
    with mock.patch.object(time, 'sleep'):
        yield


def _response(status_code=200):
    resp = mock.MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = HTTPError(response=resp)
    else:
        resp.raise_for_status.return_value = None
    return resp


def test_read_timeout_is_retried_then_succeeds():
    ok = _response()
    with mock.patch.object(server.requests, 'get',
                           side_effect=[ReadTimeout(), ReadTimeout(), ok]) as get:
        result = server._get_with_retry('http://example.com/img.jpg', timeout=(10, 30))
    assert result is ok
    assert get.call_count == 3


def test_connection_error_is_retried_then_succeeds():
    ok = _response()
    with mock.patch.object(server.requests, 'get',
                           side_effect=[ConnectionError(), ok]) as get:
        result = server._get_with_retry('http://example.com/img.jpg', timeout=(10, 30))
    assert result is ok
    assert get.call_count == 2


def test_persistent_read_timeout_gives_up_after_max_tries():
    with mock.patch.object(server.requests, 'get', side_effect=ReadTimeout()) as get:
        with pytest.raises(ReadTimeout):
            server._get_with_retry('http://example.com/img.jpg', timeout=(10, 30))
    assert get.call_count == 3


def test_http_4xx_is_not_retried():
    with mock.patch.object(server.requests, 'get',
                           return_value=_response(403)) as get:
        with pytest.raises(HTTPError):
            server._get_with_retry('http://example.com/img.jpg', timeout=(10, 30))
    assert get.call_count == 1


def test_http_5xx_is_retried():
    ok = _response()
    with mock.patch.object(server.requests, 'get',
                           side_effect=[_response(503), ok]) as get:
        result = server._get_with_retry('http://example.com/img.jpg', timeout=(10, 30))
    assert result is ok
    assert get.call_count == 2
