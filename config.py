import os

BACKEND_URL = os.environ["BACKEND_URL"]
DB_URL = os.environ["DATABASE_URL"]  # Koyeb gives you this connection string
ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]
BOOTH_PASSCODE = os.environ["BOOTH_PASSCODE"]

endpoint_url=os.environ["NEON_S3_ENDPOINT"]
aws_access_key_id=os.environ["NEON_S3_ACCESS_KEY"]
aws_secret_access_key=os.environ["NEON_S3_SECRET_KEY"]
region_name=os.environ["NEON_S3_REGION"]
BUCKET=os.environ["NEON_S3_BUCKET"]

def check():
	print(f"""
ENVIRONMENT VARIABLES

BACKEND_URL {BACKEND_URL}
DB_URL: {DB_URL}
ADMIN_API_KEY: {ADMIN_API_KEY}
BOOTH_PASSCODE: {BOOTH_PASSCODE}
endpoint_url: {endpoint_url}
aws_access_key_id: {aws_access_key_id}
aws_secret_access_key: {aws_secret_access_key}
region_name: {region_name}


        """)

