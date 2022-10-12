"""Explore."""
import flask
import sketchy


@sketchy.app.route("/explore/")
def show_explore():
    """Explore page."""
    if 'username' not in flask.session:
        flask.abort(403)
    connection = sketchy.model.get_db()
    # Query database
    logname = flask.session["username"]
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? AND NOT EXISTS(SELECT username2 "
        "FROM following"
        " WHERE username2= users.username AND username1 =?) ",
        (
            logname,
            logname,
        ),
    )
    users = cur.fetchall()
    context = {"logname": logname, "users": users}
    return flask.render_template("explore.html", **context)
