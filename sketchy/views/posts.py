"""Post."""
import arrow
import flask
import sketchy


@sketchy.app.route("/posts/<post_num>/", methods=["POST", "GET"])
def create_post(post_num):
    """Create post."""
    if flask.request.method == "POST" and 'username' not in flask.session:
        flask.abort(403)
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    # Set up connection
    connection = sketchy.model.get_db()

    logname = flask.session['username']

    cur = connection.execute(
        "SELECT postid, filename, owner, created AS timestamp, "
        "(SELECT COUNT(*) FROM likes WHERE postid=p.postid) "
        "AS numLikes, "
        "(SELECT likeid FROM likes WHERE postid=p.postid AND owner=?) "
        "AS likedPost, "
        "(SELECT filename FROM users WHERE username = p.owner) "
        "AS userFile "
        "FROM posts p "
        "WHERE postid = ?",
        (logname, post_num)
    )
    post = cur.fetchone()
    present = arrow.utcnow()
    timestamp = arrow.get(post['timestamp'])
    post['timestamp'] = timestamp.humanize(present)

    cur = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments "
        "WHERE postid= ?",
        (post_num,)
    )
    post['comments'] = cur.fetchall()
    context = {"logname": logname, "post": post}
    return flask.render_template("post.html", **context)
