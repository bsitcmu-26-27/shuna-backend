# main.py
import os
import uuid
import json
import hmac
from functools import wraps
import psycopg2
import psycopg2.extras
from app import app
from storage import upload_image, image_url, file_serve
from image_compress import compress_image
import config
from bottle import run, static_file, request, response, redirect
#from passcode import require_booth_passcode

#
# routes
import routes

#

import time
from collections import defaultdict, deque


config.check()
DB_URL = config.DB_URL
ADMIN_API_KEY = config.ADMIN_API_KEY
BOOTH_PASSCODE = config.BOOTH_PASSCODE

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_MESSAGE_LEN = 500

request_log = defaultdict(deque)

@app.route("/health")
def health_check():
    return {
        "database_connected": _check_db(),
        "database_url_length": len(os.environ.get("DATABASE_URL")),
        "booth_passcode_set": bool(os.environ.get("BOOTH_PASSCODE")),
        "booth_passcode_length": len(os.environ.get("BOOTH_PASSCODE", "")),
        "admin_key_set": bool(os.environ.get("ADMIN_API_KEY")),
    }

def _check_db():
    try:
        conn = get_conn()
        conn.close()
        return True
    except Exception:
        return False

def rate_limited(max_requests=5, window=60):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.environ.get("REMOTE_ADDR"))
            now = time.time()
            q = request_log[ip]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= max_requests:
                response.status = 429
                response.headers["Retry-After"] = str(int(window - (now - q[0])))
                return {"error": "Too many requests. Please slow down."}
            q.append(now)
            return fn(*args, **kwargs)
        return wrapper

def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(key, ADMIN_API_KEY):
            response.status = 401
            return {"error": "Invalid or missing API key."}
        return fn(*args, **kwargs)
    return wrapper

def get_conn():
    return psycopg2.connect(DB_URL)


def init_db():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                message TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT 'Anonymous yarn?',
                category TEXT NOT NULL,
                color TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                reactions INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'approved',
                media_path TEXT,
                media_name TEXT,
                x DOUBLE PRECISION NOT NULL DEFAULT 0,
                y DOUBLE PRECISION NOT NULL DEFAULT 0
            )
        """)
    conn.commit()
    conn.close()


def row_to_post(row):
    return {
        "id": str(row["id"]),
        "message": row["message"],
        "author": row["author"],
        "category": row["category"],
        "color": row["color"],
        "createdAt": row["created_at"].isoformat(),
        "reactions": row["reactions"],
        "status": row["status"],
        "isSeed": False,
        "media": (
            {"type": "image", "dataUrl": image_url(row["media_path"]), "name": "photo"}
            if row["media_path"] else None
        ),
        "x": row["x"],
        "y": row["y"],
    }


@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"


@app.route("/posts", method="OPTIONS")
@app.route("/posts/<post_id>/react", method="OPTIONS")
def cors_preflight(post_id=None):
    return {}


@app.route("/posts", method="GET")
def list_posts():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    response.content_type = "application/json"
    return json.dumps([row_to_post(r) for r in rows])


@app.route("/posts", method="POST")
def create_post():
    message = (request.forms.get("message") or "").strip()
    author = (request.forms.get("author") or "").strip() or "Anonymous yarn?"
    category = request.forms.get("category") or "other"
    color = request.forms.get("color") or "yellow"
    x = float(request.forms.get("x") or 0)
    y = float(request.forms.get("y") or 0)

    if not message:
        response.status = 400
        return {"error": "Write a thought before posting."}
    if len(message) > MAX_MESSAGE_LEN:
        response.status = 400
        return {"error": f"Keep your thought within {MAX_MESSAGE_LEN} characters."}

    media_path = None
    media_name = None
    upload = request.files.get("media")
    if upload:
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            response.status = 400
            return {"error": "Only image uploads are allowed."}
        compress_bytes, content_type = compress_image(upload.file.read())
        media_path = upload_image(compress_bytes, content_type)

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        INSERT INTO posts (message, author, category, color, media_path, media_name, x, y)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (message, author, category, color, media_path, media_name, x, y))
    row = cur.fetchone()
    conn.commit()
    conn.close()

    response.content_type = "application/json"
    return json.dumps(row_to_post(row))


@app.route("/posts/<post_id>/react", method="POST")
def react_to_post(post_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE posts SET reactions = reactions + 1 WHERE id = %s RETURNING *", (post_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if not row:
        response.status = 404
        return {"error": "Post not found."}
    response.content_type = "application/json"
    return json.dumps(row_to_post(row))

@app.route("/posts/<post_id>", method="OPTIONS")
def cors_preflight_post(post_id=None):
    return {}


@app.route("/posts/<post_id>", method="PATCH")
def update_post(post_id):
    data = request.json or {}
    fields, values = [], []

    if "status" in data:
        if data["status"] not in ("approved", "pending", "rejected"):
            response.status = 400
            return {"error": "Invalid status."}
        fields.append("status = %s")
        values.append(data["status"])
    if "x" in data:
        fields.append("x = %s")
        values.append(float(data["x"]))
    if "y" in data:
        fields.append("y = %s")
        values.append(float(data["y"]))

    if not fields:
        response.status = 400
        return {"error": "Nothing to update."}

    values.append(post_id)
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"UPDATE posts SET {', '.join(fields)} WHERE id = %s RETURNING *", values)
    row = cur.fetchone()
    conn.commit()
    conn.close()

    if not row:
        response.status = 404
        return {"error": "Post not found."}
    response.content_type = "application/json"
    return json.dumps(row_to_post(row))


@app.route("/posts/<post_id>", method="DELETE")
def delete_post(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    if not deleted:
        response.status = 404
        return {"error": "Post not found."}
    response.status = 204
    return ""

@app.route("/posts/<post_id>/position", method="OPTIONS")
def cors_preflight_position(post_id=None):
    return {}


@app.route("/posts/<post_id>/position", method="PATCH")
def update_note_position(post_id):
    data = request.json or {}
    if "x" not in data or "y" not in data:
        response.status = 400
        return {"error": "Both x and y are required."}

    try:
        x, y = float(data["x"]), float(data["y"])
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "x and y must be numbers."}

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("UPDATE posts SET x = %s, y = %s WHERE id = %s RETURNING *", (x, y, post_id))
    row = cur.fetchone()
    conn.commit()
    conn.close()

    if not row:
        response.status = 404
        return {"error": "Post not found."}
    response.content_type = "application/json"
    return json.dumps(row_to_post(row))

@app.route("/")
def root():
    return "hello! this is a backend for CMU booth... Nothing to see here i swear! >_<"

if __name__ == "__main__":
    init_db()
    run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
