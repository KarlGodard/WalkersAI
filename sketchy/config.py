"""Sketchy development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = "/"

# Secret key for encrypting cookies
SECRET_KEY = (b"\xf2\xd7h\x89\xf4\xd3u\x17\xcb\xe7J" +
              b"\n!/*\x8e\xdc\x0fNL\x99\xb9\xdfc")
SESSION_COOKIE_NAME = "login"

# File Upload to var/uploads/
SKETCHY_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = SKETCHY_ROOT / "var" / "uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/sketchy.sqlite3
DATABASE_FILENAME = SKETCHY_ROOT / "var" / "sketchy.sqlite3"
