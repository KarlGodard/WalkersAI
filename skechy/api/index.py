"""REST API for index."""
import flask
import skechy


@skechy.app.route("/api/v1/")
def get_services():
    """Return list of services."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)
