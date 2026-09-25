import requests
import config
from bottle import response, request
from functools import wraps
from log import log

def require_captcha(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.forms.get("captcha_token") or ""
        log.debug(f"[captcha] token received: {'yes, length ' + str(len(token)) if token else 'NO TOKEN'}")
        if not token:
            response.status = 400
            return {"error": "Captcha verficiation missing."}
        verify = requests.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": config.TURNSTILE_SECRET_KEY,
                    "response": token,
                    "remoteip": request.environ.get("REMOTE_ADDR"),
                    },
                timeout=5,
                )
        log.debug(f"[captcha] siteverify response: {verify.status_code} {verify.json()}")
        if not verify.json().get("success"):
            response.status = 403
            return {"error": "Captcha verification failed. Try again dawg."}
        log.debug("[captcha] passed, calling create_post")
        return fn(*args, **kwargs)
    return wrapper


