from .syndicate_models import *
from .other_models import *

# Django deletes a user's rows only in the tables of models it has imported, and
# outside a web request only this module is sure to be: `manage.py shell`, for
# one, never loads the URL conf that imports app.jusprin.
from app.jusprin.models import JusPrinAICredit, JusPrinChat  # noqa: E402,F401
