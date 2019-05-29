
import json

# Return dict if not empty, otherwise None.
def dict_or_none(dict_value):
    return dict_value if dict_value else None

def set_as_str_if_present(target_dict, source_dict, key, target_key=None):
    if source_dict.get(key):
        if not target_key:
            target_key = key
        target_dict[target_key] = json.dumps(source_dict.get(key))
