"""Delete."""
import flask
import sketchy


@sketchy.app.route("/accounts/delete/", methods=["POST", "GET"])
def delete_page():
    """Delete page."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    sketchy.model.get_db()
    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("delete.html", **context)
