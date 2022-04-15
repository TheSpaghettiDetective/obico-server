import logging
import functools
from raven.contrib.django.raven_compat.models import client as sentryClient
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
            sentryClient.captureException()
            raise
    return wrapper
