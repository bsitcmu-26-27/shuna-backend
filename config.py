import os
import logging as log
from sys import exit

BACKEND_URL = os.environ["BACKEND_URL"]
DB_URL = os.environ["DATABASE_URL"] 
#ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]
#BOOTH_PASSCODE = os.environ["BOOTH_PASSCODE"]

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
else:
    PROD_MODE=os.environ["PROD_MODE"]


def check():
    if TURNSTILE_SECRET_KEY == "1x0000000000000000000000000000000AA":
        log.warning("Using test key. Do not use in branch")
        if PROD_MODE != None:
            log.error("Currently in production, Not continuing")
            exit(1)
    print(f"""
ENVIRONMENT VARIABLES

BACKEND_URL {BACKEND_URL}
DB_URL: {DB_URL}
TURNSTILE_SECRET_KEY: {TURNSTILE_SECRET_KEY}
endpoint_url: {endpoint_url}
aws_access_key_id: {aws_access_key_id}
aws_secret_access_key: {aws_secret_access_key}
region_name: {region_name}

        """)

