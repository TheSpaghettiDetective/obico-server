import dataclasses
import json
import time
import re
import random
import string

from lib.cache import (
    set_value_by_one_time_passcode,
    lookup_value_by_one_time_passcode,
)

# Handshake via a map: one_time_passcode -> verification_code
#   one_time_passcode not exited: no device for this one_time_passcode
#   one_time_passcode: '': empty means no user has verified this one_time_passcode
#   one_time_passcode: 'verification_code': means this one_time_passcode has been verified by a user having this verification_code

def request_one_time_passcode(one_time_passcode: str, code_length=5) -> str:
    verification_code = lookup_value_by_one_time_passcode(one_time_passcode)
    if verification_code is None: # one_time_passcode not existed in cache
        letters_and_digits = string.ascii_letters + string.digits
        new_code = ''.join(random.choice(letters_and_digits) for _ in range(code_length)).lower()
        set_value_by_one_time_passcode(new_code, 60*60*2, '') # one time passcode has a ttl of 2 hours
        return (new_code, '')
    else:
        return (one_time_passcode, verification_code) # verification_code may be an empty string in this case

def check_one_time_passcode(one_time_passcode, verification_code) -> str:
    existing_verification_code = lookup_value_by_one_time_passcode(one_time_passcode)
    if existing_verification_code is None: # one_time_passcode not existed in cache
        return False # one_time_passcode not existed. Verification failed
    elif existing_verification_code == '':
        set_value_by_one_time_passcode(one_time_passcode, 60, verification_code) # Printer is expected to consume this fairly quickly on the next poll. Set a short ttl to make it more secure
        return True
    else:
        return False