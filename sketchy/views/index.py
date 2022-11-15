"""
Insta485 index (main) view.

URLs include:
/
"""
# import os
import arrow
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

@sketchy.app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    connection = sketchy.model.get_db()
    req = flask.request.get_json(silent=True, force=True)
    fulfillmentText = ''
    query_result = req.get('queryResult')
    if query_result.get('action') == 'get.painter':
        ### Perform set of executable code
        ### if required
        ###
        parameters = query_result.get('parameters')
        painting_name = parameters['painting']
        cur = connection.execute(
        "SELECT ai.displayName "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE aw.title= ?",
        (painting_name,)
        )
        painter_name = cur.fetchone()
        
        fulfillmentText = painter_name['displayName'] + " painted the " + painting_name
    if query_result.get('action') == 'get.nationality':
        painter_name = query_result.get('parameters')['artist']
        cur = connection.execute(
        "SELECT ai.nationality "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE ai.displayName = ?",
        (painter_name,)
        )
        nationality = cur.fetchone()
        fulfillmentText = painter_name + " is " + nationality['nationality']
    if query_result.get('action') == 'get.medium':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.medium "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE aw.title = ?",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The " + painting_name + " was painted with " + item['medium']
    if query_result.get('action') == 'get.dimensions':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.dimensions "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE aw.title = ?",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The " + painting_name + " has dimensions of " + item['dimensions']
    if query_result.get('action') == 'get.yearPainted':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.date "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE aw.title = ?",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The " + painting_name + " was painted in " + item['date']
    if query_result.get('action') == 'get.beginDate':
        artist_name = query_result.get('parameters')['artist']
        cur = connection.execute(
        "SELECT ai.beginDate "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE ai.displayName = ?",
        (artist_name,)
        )
        item = cur.fetchone()
        fulfillmentText = artist_name + " began his career in " + str(item['beginDate'])
    if query_result.get('action') == 'get.endDate':
        artist_name = query_result.get('parameters')['artist']
        cur = connection.execute(
        "SELECT ai.endDate "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE ai.displayName = ?",
        (artist_name,)
        )
        item = cur.fetchone()
        fulfillmentText = artist_name + " stopped his career in " + str(item['endDate'])
    return {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }


@sketchy.app.route("/uploads/<filename>")
def upload_file(filename):
    """Upload file."""
    if 'username' not in flask.session:
        flask.abort(403)

    upload_folder = sketchy.app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, filename)
