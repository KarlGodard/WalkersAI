"""Logging in and out."""
import flask
import skechy


@skechy.app.route('/accounts/login/')
def login():
    """Show the login page."""
    # POST-only route for handling login requests
    return flask.render_template("login.html")


@skechy.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """Logout."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    # POST-only route for handling logout requests
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))
