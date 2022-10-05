"""
Insta485 index (main) view.

URLs include:
/users/<user_url_slug>
"""

import os
import pathlib
import uuid
import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/")
def show_user(user_url_slug):
    """Handle if user is following or not."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))

    connection = insta485.model.get_db()
    # Check if the user_url_slug is in the database
    # aborts 404 if not
    cur = connection.execute(
        "SELECT username FROM users WHERE username=?",
        (user_url_slug, )
    )
    check_user = cur.fetchone()

    logname = flask.session['username']

    if check_user is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT username1 " " FROM following "
        " WHERE username1=? " "AND username2=?",
        (
            logname,
            user_url_slug,
        ),
    )

    user_following = len(cur.fetchall())
    posts = connection.execute(
        "SELECT * " " FROM posts " "WHERE owner=?", (user_url_slug,)
    )
    posts = posts.fetchall()
    fullname = connection.execute(
        "SELECT fullname" " FROM users " " WHERE username=?", (user_url_slug,)
    )
    fullname = fullname.fetchall()
    num_posts = len(posts)

    num_followers = connection.execute(
        "SELECT * " " FROM following" " WHERE username2=?", (user_url_slug,)
    )
    num_followers = len(num_followers.fetchall())
    num_following = connection.execute(
        "SELECT * " " FROM following" " WHERE username1=?", (user_url_slug,)
    )
    num_following = len(num_following.fetchall())

    context = {
        "logname": logname,
        "user_following": user_following,
        "username": user_url_slug,
        "num_posts": num_posts,
        "posts": posts,
        "fullname": fullname[0]["fullname"],
        "num_followers": num_followers,
        "num_following": num_following,
    }
    return flask.render_template("user.html", **context)


@insta485.app.route("/following/", methods=["POST"])
def handle_follow_user():
    """Follow or unfollow user."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    filename = flask.request.args.get("target")

    connection = insta485.model.get_db()

    logname = flask.session["username"]
    if flask.request.form["operation"] == "follow":
        connection.execute(
            "INSERT INTO following(username1,username2) " " VALUES(?,?) ",
            (logname, flask.request.form["username"]),
        )

    else:
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2= ?",
            (logname, flask.request.form["username"]),
        )
    return flask.redirect(filename)


@insta485.app.route("/posts/", methods=["POST"])
def upload_img():
    """Upload image."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["username"]

    filename = flask.request.args.get("target")
    if filename is None:
        filename = "/users/" + logname + "/"

    connection = insta485.model.get_db()
    if flask.request.form["operation"] == "create":
        file = flask.request.files["file"]
        if file.filename == "":
            flask.abort(400)
        # Compute base name (filename without directory).
        # We use a UUID to avoid
        # clashes with existing files, and ensure that the
        # name is compatible with the
        # filesystem.
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(file.filename).suffix
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename

        file.save(path)
        connection.execute(
            "INSERT INTO posts(filename, owner)" "VALUES(?,?)",
            (
                uuid_basename,
                logname,
            ),
        )
    else:
        cur = connection.execute(
            "SELECT filename FROM posts WHERE postid=?",
            (flask.request.form['postid'],)
        )
        file = cur.fetchone()

        file_path = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"], file['filename'])
        os.remove(file_path)
        connection.execute(
            "DELETE FROM posts WHERE postid=? ",
            (flask.request.form['postid'], )
        )
        cur = connection.execute(
            "SELECT * FROM posts"
        )
        return flask.redirect(filename)
    return flask.redirect(filename)
