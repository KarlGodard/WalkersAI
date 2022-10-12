"""Password."""
import flask
import sketchy


@sketchy.app.route("/accounts/password/")
def change_password():
    """Change password."""
    # Query database
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("password.html", **context)
