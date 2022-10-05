"""
Insta485 followers view.

URLs include:
/users/<user_url_slug>/followers
"""
import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/followers/")
def show_followers(user_url_slug):
    """Display / route."""
    # Connect to database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    connection = insta485.model.get_db()
    # Query database
    logname = flask.session["username"]

    cur = connection.execute(
        "SELECT * " "FROM users WHERE username=?", (user_url_slug,)
    )
    user_info = cur.fetchone()

    # Abort 404 if the user_url_slug is not in the database
    if user_info is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT username, filename, "
        # Is none if logged in user doesn't follow user
        "(SELECT username1 FROM following "
        "WHERE username2=username AND username1=?) AS relationship "
        "FROM users "
        "WHERE username IN "
        "(SELECT username1 FROM following WHERE username2= ?) ",
        (logname, user_url_slug),
    )
    followers = cur.fetchall()

    context = {
        "logname": logname,
        "user_url_slug": user_url_slug,
        "followers": followers,
    }

    if "username" in flask.session:
        return flask.render_template("followers.html", **context)
    return flask.redirect(flask.url_for("login"))
