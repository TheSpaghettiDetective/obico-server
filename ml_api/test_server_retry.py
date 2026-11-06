import sys
import time
from unittest import mock

import pytest
import requests
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

# Stub the model loader so importing server.py doesn't require darknet weights
sys.modules.setdefault('lib.detection_model', mock.MagicMock())

import server  # noqa: E402
import deadline  # noqa: E402


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


def test_expired_deadline_returns_503_without_fetch_or_inference():
    with mock.patch.object(server.requests, 'get') as get, \
            mock.patch.object(server, 'detect') as detect:
        response = server.app.test_client().get(
            '/p/?img=http://example.com/img.jpg',
            headers={'X-Deadline': str(time.time() - 1)},
        )
    assert response.status_code == 503
    assert response.json['detections'] == []
    get.assert_not_called()
    detect.assert_not_called()


def test_deadline_fetch_caps_connect_and_read_timeouts():
    now = time.time()
    ok = _response()
    with mock.patch.object(deadline.requests, 'get', return_value=ok) as get:
        result = deadline.get_with_deadline('http://example.com/img.jpg', now + 2, (10, 30))
    assert result is ok
    connect, read = get.call_args.kwargs['timeout']
    assert 0 < connect <= 2
    assert 0 < read <= 2


def test_deadline_fetch_does_not_retry_after_expiry():
    clock = [100.0]

    def timeout_once(*args, **kwargs):
        clock[0] = 103.0
        raise ReadTimeout()

    with mock.patch.object(deadline.time, 'time', side_effect=lambda: clock[0]), \
            mock.patch.object(deadline.requests, 'get', side_effect=timeout_once) as get:
        with pytest.raises(deadline.DeadlineExpired):
            deadline.get_with_deadline('http://example.com/img.jpg', 102.0, (10, 30))
    assert get.call_count == 1


def test_gcs_session_is_reused_within_worker_and_recreated_after_fork():
    sessions = [mock.MagicMock(), mock.MagicMock()]
    with mock.patch.object(deadline, '_gcs_session', None), \
            mock.patch.object(deadline, '_gcs_session_pid', None), \
            mock.patch.object(deadline.os, 'getpid', side_effect=[11, 11, 12]), \
            mock.patch.object(deadline.requests, 'Session', side_effect=sessions) as create:
        for _ in range(3):
            deadline.get_image('https://storage.googleapis.com/bucket/image.jpg', timeout=(1, 2))
    assert create.call_count == 2
    assert sessions[0].get.call_count == 2
    assert sessions[1].get.call_count == 1


def test_legacy_gcs_request_without_deadline_keeps_requests_get():
    ok = _response()
    with mock.patch.object(deadline, '_gcs_session', None), \
            mock.patch.object(deadline, '_gcs_session_pid', None), \
            mock.patch.object(deadline.requests, 'Session') as session, \
            mock.patch.object(server.requests, 'get', return_value=ok) as get:
        result = server._get_with_retry(
            'https://storage.googleapis.com/bucket/image.jpg', timeout=(10, 30))
    assert result is ok
    get.assert_called_once()
    session.assert_not_called()
