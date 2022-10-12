"""Password."""
import flask
import skechy


@skechy.app.route("/accounts/password/")
def change_password():
    """Change password."""
    # Query database
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template("password.html", **context)
