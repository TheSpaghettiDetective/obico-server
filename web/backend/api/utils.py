import logging
import functools
from sentry_sdk import capture_exception
from rest_framework.exceptions import ValidationError

LOGGER = logging.getLogger(__name__)


def report_validationerror(f):
    # by default ValidationError is silenced (for good reason);
    # use this decorator where ValidationError is
    # a sign of bug, broken contract or something suspicious
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError:
            LOGGER.exception('validationerror')
            capture_exception()
            raise
    return wrapper
