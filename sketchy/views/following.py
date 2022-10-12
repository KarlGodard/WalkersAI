"""
Insta485 following view.

URLs include:
/users/<user_url_slug>/following
"""
import flask
import sketchy


@sketchy.app.route("/users/<user_url_slug>/following/")
def show_following(user_url_slug):
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    # Query database
    logname = flask.session['username']

    connection = sketchy.model.get_db()
    cur = connection.execute(
        "SELECT username FROM users " " WHERE username=?",
        (user_url_slug, )
    )
    user_info = cur.fetchall()[0]

    # Abort 404 if the user_url_slug is not in the database
    if not user_info:
        flask.abort(404)

    cur = connection.execute(
        "SELECT username, filename, "
        # Is none if logged in user doesn't follow user
        "(SELECT username1 FROM following "
        "WHERE username1=username AND username2=?) AS relationship, "
        "(SELECT username1 FROM following "
        "WHERE username1=? AND username2=username) AS loggedInRelationship "
        "FROM users "
        "WHERE username IN "
        "(SELECT username2 FROM following WHERE username1= ?) ",
        (user_url_slug, logname, user_url_slug),
    )
    following = cur.fetchall()

    context = {
        "logname": logname,
        "user_url_slug": user_url_slug,
        "following": following,
    }

    if "username" in flask.session:
        return flask.render_template("following.html", **context)
    return flask.redirect(flask.url_for("login"))
