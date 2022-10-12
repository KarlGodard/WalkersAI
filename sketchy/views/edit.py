"""Edit."""
import flask
import sketchy


@sketchy.app.route("/accounts/edit/", methods=["POST", "GET"])
def edit_profile():
    """Edit profile."""
    connection = sketchy.model.get_db()
    # Query database
    logname = flask.session['username']
    cur = connection.execute(
        "SELECT username, email, filename, fullname "
        "FROM users "
        "WHERE username = ? ",
        (logname,)
    )
    user = cur.fetchone()
    context = user
    context["logname"] = logname
    return flask.render_template("edit.html", **context)
