"""Sketchy package initializer."""
import flask
import pymongo
import bcrypt

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (skechy/config.py)
app.config.from_object("sketchy.config")

# Overlay settings read from a Python file whose path is set in the environment
# variable SKETCHY_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export SKETCHY_SETTINGS=secret_key_config.py
app.config.from_envvar("SKETCHY_SETTINGS", silent=True)

client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test")
db = client.sketchy
records = db.users

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import sketchy.views  # noqa: E402  pylint: disable=wrong-import-position
import sketchy.model  # noqa: E402  pylint: disable=wrong-import-position
import sketchy.api  # noqa: E402  pylint: disable=wrong-import-position
