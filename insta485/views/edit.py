"""Edit."""
import flask
import insta485


@insta485.app.route("/accounts/edit/", methods=["POST", "GET"])
def edit_profile():
    """Edit profile."""
    connection = insta485.model.get_db()
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
