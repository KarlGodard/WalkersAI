"""
Insta485 index (main) view.

URLs include:
/
"""
# import os
import arrow
import flask
import insta485


@insta485.app.route("/comments/", methods=["POST"])
def handle_comment():
    """Add comment to a post."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))

    filename = flask.request.args.get("target")
    if not filename:
        filename = flask.url_for("show_index")
    # Handles the comment button being clicked
    connection = insta485.model.get_db()

    # Make insert query to add comment to database
    if flask.request.form["operation"] == "create":
        connection.execute(
            "INSERT INTO "
            "comments(owner, postid, text)"
            "VALUES(?, CAST(? AS int), ?)",
            (
                flask.session["username"],
                flask.request.form["postid"],
                flask.request.form["text"],
            ),
        )
    else:
        connection.execute(
            "DELETE FROM comments " " WHERE commentid=?",
            (flask.request.form["commentid"]),
        )
    return flask.redirect(filename)


@insta485.app.route("/likes/", methods=["POST"])
def handle_like():
    """Add or remove like from post."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    filename = flask.request.args.get("target")
    # Handles the like or unlike button being clicked
    connection = insta485.model.get_db()

    # Make query to add or remove like from post
    if flask.request.form["operation"] == "like":
        like = connection.execute(
            "SELECT * " "FROM likes " "WHERE owner=? " " AND postid=?",
            (
                flask.session["username"],
                flask.request.form["postid"],
            ),
        )
        like = like.fetchall()
        if len(like) != 0:
            # duplicate like
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) " " VALUES(?, CAST(? AS int))",
            (
                flask.session["username"],
                flask.request.form["postid"],
            ),
        )
    else:
        like = connection.execute(
            "SELECT * " "FROM likes " "WHERE owner=? " " AND postid=?",
            (
                flask.session["username"],
                flask.request.form["postid"],
            ),
        )
        like = like.fetchall()
        if len(like) == 0:
            # duplicate unlike
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE owner=? AND postid=? ",
            (
                flask.session["username"],
                flask.request.form["postid"],
            ),
        )

    return flask.redirect(filename)


@insta485.app.route("/")
def show_index():
    """Display / route."""
    if "username" in flask.session:
        # Connect to database
        connection = insta485.model.get_db()
        # Query database
        logname = flask.session["username"]

        cur = connection.execute(
            # Gets info about each post, uses timestamp as alias for created
            "SELECT postid, filename, owner, created AS timestamp, "
            # Gets the number of like for each post
            "(SELECT COUNT(*) FROM likes WHERE postid=p.postid) AS numLikes, "
            # Stores the likeid if a like from the user exists for post
            # Used to determine if like or unlike button displays
            "(SELECT likeid FROM likes "
            "WHERE postid=p.postid AND owner=?) AS likedPost, "
            # Gets the name of each user's profile pic file
            "(SELECT filename FROM users "
            " WHERE username = owner) AS userFile "
            "FROM posts p "
            # Only gets posts from users
            # that the current user is following
            # For each key in following,
            # (username1, username2) => user1 follows user2
            "WHERE owner IN (SELECT username2 "
            " FROM following WHERE username1 = ?) OR owner=? "
            "ORDER BY postid DESC "
            "LIMIT 99999",
            (
                logname,
                logname,
                logname,
            ),
        )
        posts = cur.fetchall()
        # Add database info to context
        # context = {"logname": logname, "users": users}

        for post in posts:
            # Get all the comments for each post
            cur = connection.execute(
                "SELECT commentid, owner, text "
                " FROM comments "
                " WHERE postid=?"
                "ORDER BY commentid",
                (post["postid"],),
            )
            post["comments"] = cur.fetchall()
            # Handle timestamp for each post
            present = arrow.utcnow()
            timestamp = arrow.get(post["timestamp"])
            post["timestamp"] = timestamp.humanize(present)

        context = {"logname": logname, "posts": posts}

        return flask.render_template("index.html", **context)
    return flask.redirect(flask.url_for("login"))


@insta485.app.route("/uploads/<filename>")
def upload_file(filename):
    """Upload file."""
    if 'username' not in flask.session:
        flask.abort(403)

    upload_folder = insta485.app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, filename)
