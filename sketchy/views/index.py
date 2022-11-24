"""
Insta485 index (main) view.

URLs include:
/
"""
# import os
import flask
import sketchy


@sketchy.app.route("/comments/", methods=["POST"])
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
    connection = sketchy.model.get_db()

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


@sketchy.app.route("/likes/", methods=["POST"])
def handle_like():
    """Add or remove like from post."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    filename = flask.request.args.get("target")
    # Handles the like or unlike button being clicked
    connection = sketchy.model.get_db()

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


@sketchy.app.route("/")
def show_index():
    
    context = {"logname": "Nate"}
    
    return flask.render_template("index.html", **context)


@sketchy.app.route("/uploads/<filename>")
def upload_file(filename):
    """Upload file."""
    if 'username' not in flask.session:
        flask.abort(403)

    upload_folder = sketchy.app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, filename)
