"""Optional caller deadlines for ML image requests."""

import math
import os
import time
from urllib.parse import urlsplit

import requests
from requests.exceptions import HTTPError


class DeadlineExpired(Exception):
    pass


_gcs_session = None
_gcs_session_pid = None


def get_image(url, **kwargs):
    """Reuse GCS connections, creating the session only after worker fork."""
    global _gcs_session, _gcs_session_pid
    if urlsplit(url).hostname != 'storage.googleapis.com':
        return requests.get(url, **kwargs)
    pid = os.getpid()
    if _gcs_session is None or _gcs_session_pid != pid:
        _gcs_session = requests.Session()
        _gcs_session_pid = pid
    return _gcs_session.get(url, **kwargs)


def parse_deadline(raw):
    if raw is None:
        return None
    try:
        deadline = float(raw)
    except ValueError as exc:
        raise ValueError('X-Deadline must be a Unix timestamp') from exc
    if not math.isfinite(deadline):
        raise ValueError('X-Deadline must be a finite Unix timestamp')
    return deadline


def expired(deadline):
    return deadline is not None and time.time() >= deadline


def _retryable(exc):
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    return isinstance(exc, HTTPError) and exc.response is not None and exc.response.status_code >= 500


def get_with_deadline(url, deadline, timeout):
    """Fetch an image with at most one immediate retry while time remains.

    `requests` read timeouts apply to each socket read rather than the whole
    download, so callers must check the deadline again after reading content.
    """
    for attempt in range(2):
        remaining = deadline - time.time()
        if remaining <= 0:
            raise DeadlineExpired()
        bounded_timeout = (min(timeout[0], remaining), min(timeout[1], remaining))
        try:
            response = get_image(url, timeout=bounded_timeout)
            response.raise_for_status()
            if expired(deadline):
                response.close()
                raise DeadlineExpired()
            return response
        except (HTTPError, requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            if not _retryable(exc) or attempt == 1:
                if expired(deadline):
                    raise DeadlineExpired() from exc
                raise
