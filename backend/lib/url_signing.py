import base64
import hashlib
from datetime import timedelta

from django.utils import timezone
from urllib.parse import urlparse, parse_qs, urlunparse, ParseResult
from dataclasses import dataclass, field, InitVar
from typing import Optional, List, Union
import hmac
from django.conf import settings
import logging

LOGGER = logging.getLogger(__name__)


def calculate_hmac_digest(path: str):
    """Returns base64 encoded digest given a 'path'"""
    digest = hmac.digest(
        key=settings.SECRET_KEY.encode(),
        msg=path.encode(),
        digest=hashlib.sha256
    )
    return base64.urlsafe_b64encode(str(digest).encode()).decode()


def new_signed_url(url_str: str) -> str:
    """
    Signs a URL based on a given

    Signature is appended in the form of URL parameters in the query string. Note that
    the entire query string will be replaced (everything after '?' in the URL).
    """
    parsed_url = urlparse(url_str)
    digest = calculate_hmac_digest(parsed_url.path)
    signed_url = parsed_url._replace(query=f"digest={digest}")
    return urlunparse(signed_url)


@dataclass
class HmacSignedUrl:
    """This dataclass provides functions to check the validity of an HMAC signed url"""
    url_str: InitVar[str]

    # Calculated fields are set during __post_init__
    path: str = field(init=False)
    supplied_digest: str = field(init=False)

    # Internal fields (don't show in repr)
    _parsed_url: ParseResult = field(init=False, repr=False)
    _url_params: dict = field(init=False, repr=False)

    def __post_init__(self, url_str: str):
        self._parsed_url = urlparse(url_str)
        self._url_params = parse_qs(self._parsed_url.query)
        self.path = self._parsed_url.path
        self.supplied_digest = self._get_single_url_param('digest', None)
        if self.supplied_digest is None:
            raise ValueError("Must supply a 'digest' parameter to check authorization")

    def _get_single_url_param(self, key: str, default=None) -> str:
        """
        Returns first URL parameter value by key name, or (default) if empty.

        This function is necessary because parse_qs() returns a dictionary of lists
        since urls can contain duplicate query parameters.
        """
        vals: List = self._url_params.get(key, [])
        return vals[0] if vals else default

    def is_authorized(self) -> bool:
        """Returns True if the supplied digest matches the calculated digest, else False"""
        calculated_digest = calculate_hmac_digest(path=self.path)
        return hmac.compare_digest(self.supplied_digest, calculated_digest)
