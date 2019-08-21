
import json
from django.conf import settings

# Return dict if not empty, otherwise None.
def dict_or_none(dict_value):
    return dict_value if dict_value else None

def set_as_str_if_present(target_dict, source_dict, key, target_key=None):
    if source_dict.get(key):
        if not target_key:
            target_key = key
        target_dict[target_key] = json.dumps(source_dict.get(key))

def ml_api_auth_headers():
    return {"Authorization": "Bearer {}".format(settings.ML_API_TOKEN)} if settings.ML_API_TOKEN else {}
