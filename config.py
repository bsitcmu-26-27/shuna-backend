import os
from log import log
from sys import exit


try:
    os.environ["BACKEND_URL"]
except:
    BACKEND_URL = "http://localhost:8000"
    log.info(f"Running locally at: {BACKEND_URL}")
else:
    BACKEND_URL = os.environ["BACKEND_URL"]
    log.info(f"Running non-local backend at {BACKEND_URL}")

DB_URL = os.environ["DATABASE_URL"]
try:
    os.environ["TURNSTILE_SECRET_KEY"]
except:
    TURNSTILE_SECRET_KEY="1x0000000000000000000000000000000AA"
else:
    TURNSTILE_SECRET_KEY = os.environ["TURNSTILE_SECRET_KEY"]
endpoint_url=os.environ["NEON_S3_ENDPOINT"]
aws_access_key_id=os.environ["NEON_S3_ACCESS_KEY"]
aws_secret_access_key=os.environ["NEON_S3_SECRET_KEY"]
region_name=os.environ["NEON_S3_REGION"]
BUCKET=os.environ["NEON_S3_BUCKET"]

try:
    os.environ["PROD_MODE"]
except:
    PROD_MODE = None
    log.info("Running locally. PROD_MODE is not set.")
else:
    PROD_MODE=os.environ["PROD_MODE"]
    log.info("Running on Production Mode.")


def check():
    if TURNSTILE_SECRET_KEY == "1x0000000000000000000000000000000AA":
        log.warning("Using test key. Do not use in branch")
        if PROD_MODE != None and os.environ["USER"] == "cmu-bsit":
            log.error("Currently in production, Not continuing")
            exit(1)

    log.debug(f"""
ENVIRONMENT VARIABLES

BACKEND_URL {BACKEND_URL}
DB_URL: {DB_URL}
TURNSTILE_SECRET_KEY: {TURNSTILE_SECRET_KEY}
endpoint_url: {endpoint_url}
aws_access_key_id: {aws_access_key_id}
aws_secret_access_key: {aws_secret_access_key}
region_name: {region_name}

        """)

