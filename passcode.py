from functools import wraps
from bottle import request
import hmac
import os
BOOTH_PASSCODE = os.environ["BOOTH_PASSCODE"]

def require_booth_passcode(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        passcode = request.forms.get("passcode") or ""
        if not hmac.compare_digest(passcode, BOOTH_PASSCODE):
            response.status = 403
            return {"error": "Incorrect booth passcode."}
        return fn(*args, **kwargs)
    return wrapper

