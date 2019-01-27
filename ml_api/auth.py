import os
from functools import wraps
from flask import Flask, request, Response

ML_API_TOKEN=os.environ.get("ML_API_TOKEN")

def token_required(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if request.headers.get("Authorization") == 'Bearer {}'.format(ML_API_TOKEN):
            return f()
        else:
            return Response(status=401)

    @wraps(f)
    def passthru(*args, **kwargs):
        return f()

    if ML_API_TOKEN:
        return check_authorization
    else:
        return passthru
