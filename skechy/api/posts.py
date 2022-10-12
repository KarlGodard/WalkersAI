"""REST API for posts."""
import hashlib
import flask
import skechy


def login(connection):
    """Login."""
    context = {
        "message": "Forbidden",
        "status_code": 403,
    }
    if "username" in flask.session:
        username = flask.session["username"]
        return username
    if (
        flask.request.authorization
        and "username" in flask.request.authorization
        and "password" in flask.request.authorization
    ):
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
    else:
        return context
    curr_password = connection.execute(
        "SELECT password " "FROM users " "WHERE username = ?",
        (username,),
    ).fetchone()
    if curr_password is None:
        return context
    salt = curr_password["password"].split("$")[1]

    algorithm = "sha512"
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()

    if password_hash != curr_password["password"].split("$")[2]:
        return context

    flask.session["username"] = username
    return username


@skechy.app.route("/api/v1/posts/")
def get_newest_posts():
    """Get newest posts."""
    bad_request = {
        "message": "Bad Request",
        "status_code": 400,
    }
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    if size < 0 or page < 0:
        return flask.jsonify(**bad_request), 400
    # fix negative values for size and page
    postid_lte = flask.request.args.get("postid_lte", type=int)
    connection = skechy.model.get_db()
    if postid_lte:
        posts = connection.execute(
            "SELECT postid"
            " FROM posts "
            " WHERE postid<=? "
            " AND (owner=? "
            " OR owner IN "
            "(SELECT username2 FROM following WHERE username1=?)) "
            " ORDER BY postid DESC "
            " LIMIT ? OFFSET ?",
            (
                postid_lte,
                logname,
                logname,
                size,
                page * size,
            ),
        )
    else:
        max_post_id = connection.execute(
            "SELECT MAX(postid) " " AS max_id " " FROM posts"
        ).fetchone()
        postid_lte = max_post_id["max_id"]
        posts = connection.execute(
            "SELECT postid"
            " FROM posts"
            " WHERE (owner=? "
            " OR owner IN "
            "(SELECT username2 FROM following WHERE username1=?)) "
            " ORDER BY postid DESC "
            " LIMIT ? OFFSET ?",
            (
                logname,
                logname,
                size,
                page * size,
            ),
        )
    posts = posts.fetchall()
    results = []
    for post in posts:
        results.append(
            {
                "postid": int(post["postid"]),
                "url": "/api/v1/posts/" + str(post["postid"]) + "/",
            }
        )

    url = (flask.request.full_path).rstrip("?")

    if len(posts) < size:
        nxt = ""
    else:
        nxt = (
            "/api/v1/posts/?size="
            + str(size)
            + "&page="
            + str(page + 1)
            + "&postid_lte="
            + str(postid_lte)
        )

    context = {
        "next": nxt,
        "results": results,
        "url": url,
    }
    return flask.jsonify(**context)


@skechy.app.route("/api/v1/posts/<int:postid_url_slug>/")
def get_post(postid_url_slug):
    """Return post on postid.

    Example:
    {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": "/posts/1/",
      "url": "/api/v1/posts/1/"
    }
    """
    not_found = {
        "message": "Not found",
        "status_code": 404,
    }
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403
    context = {}
    comments_list = []
    comments = connection.execute(
        "SELECT * from comments WHERE postid=?", (postid_url_slug,)
    ).fetchall()
    post = connection.execute(
        "SELECT * from posts WHERE postid=?", (postid_url_slug,)
    ).fetchone()
    if not post:
        return flask.jsonify(**not_found), 404
    for comment in comments:
        comments_list.append(
            {
                "commentid": comment["commentid"],
                "lognameOwnsThis": logname == comment["owner"],
                "owner": comment["owner"],
                "ownerShowUrl": f"/users/{comment['owner']}/",
                "text": comment["text"],
                "url": f"/api/v1/comments/{comment['commentid']}/",
            }
        )
    context["comments"] = comments_list
    context["created"] = post["created"]
    context["imgUrl"] = f"/uploads/{post['filename']}"
    context["owner"] = post["owner"]
    context["ownerShowUrl"] = f"/users/{post['owner']}/"
    context["postShowUrl"] = f"/posts/{postid_url_slug}/"
    context["postid"] = postid_url_slug
    context["url"] = flask.request.path
    print(flask.request.url)

    likes = connection.execute(
        "SELECT * from likes WHERE postid=?",
        (postid_url_slug,),
    ).fetchall()

    logname_likes_this = False
    logname_like_id = -1
    for like in likes:
        if like["owner"] == logname:
            logname_likes_this = True
            logname_like_id = like["likeid"]
    if logname_like_id != -1:
        like_url = f"/api/v1/likes/{logname_like_id}/"
    else:
        like_url = None
    context["likes"] = {
        "numLikes": len(likes),
        "lognameLikesThis": logname_likes_this,
        "url": like_url,
    }

    owner = connection.execute(
        "SELECT * " "FROM users WHERE username=?", (post["owner"],)
    )
    owner = owner.fetchone()

    context["ownerImgUrl"] = f"/uploads/{owner['filename']}"

    return flask.jsonify(**context)


# Deals with adding a like to a post


@skechy.app.route("/api/v1/likes/", methods=["POST"])
def like_post():
    """Like post."""
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403
    postid = flask.request.args.get("postid", type=int)
    not_found = {
        "message": "Not found",
        "status_code": 404,
    }
    if postid:
        cur = connection.execute(
            "SELECT * " "FROM posts WHERE postid=?", (postid,)
        ).fetchall()
        if len(cur) == 0:
            return flask.jsonify(**not_found), 404
        cur = connection.execute(
            "SELECT * FROM likes WHERE owner=? AND postid=?",
            (
                logname,
                postid,
            ),
        )
        like = cur.fetchone()
        if like is None:
            # No duplicate like, so create new one
            # print("ATTEMPTING TO ADD LIKE")
            connection.execute(
                "INSERT INTO likes(owner, postid) " "VALUES(?, ?)",
                (
                    logname,
                    postid,
                ),
            )
            cur = connection.execute(
                "SELECT * FROM likes WHERE rowid=last_insert_rowid()"
            )
            like_info = cur.fetchone()
            # print(like_info)
            # {
            # "likeid": 6,
            # "url": "/api/v1/likes/6/"
            # }
            # print("MAKING CONTEXT")
            context = {
                "likeid": str(like_info["likeid"]),
                "url": "/api/v1/likes/" + str(like_info["likeid"]) + "/",
            }
            # print(context)
            # Return 201 code
            return flask.jsonify(**context), 201
        # Duplicate like, so return it and don't create new one
        # {
        # "likeid": 6,
        # "url": "/api/v1/likes/6/"
        # }
        context = {
            "likeid": like["likeid"],
            "url": "/api/v1/likes/" + str(like["likeid"]) + "/",
        }
        return flask.jsonify(**context), 200
    return flask.jsonify(**not_found), 404


# Deals with deleting a like from a post


@skechy.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Delete like."""
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403

    cur = connection.execute("SELECT * FROM likes WHERE likeid=?", (likeid,))
    like_info = cur.fetchone()

    if like_info is None:
        # likeid does not exist
        # print("LIKE DOESN'T EXIST")
        return flask.Response(status=404)

    if like_info["owner"] != logname:
        # Logged in user does not own the like
        return flask.Response(status=403)

    connection.execute("DELETE FROM likes WHERE likeid=?", (likeid,))
    # print("LIKE DELETED")
    # context = {}
    # Like successfully deleted
    # return flask.jsonify(**context), 204
    return flask.Response(status=204)


# Deals with adding a comment
@skechy.app.route("/api/v1/comments/", methods=["POST"])
def comment_post():
    """Comment post."""
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403
    postid = flask.request.args.get("postid", type=int)
    content = flask.request.json
    text = content["text"]

    if postid:
        connection.execute(
            "INSERT INTO comments(owner, postid, text) " "VALUES(?, ?, ?) ",
            (logname, postid, text),
        )

        cur = connection.execute(
            "SELECT * FROM comments WHERE rowid=last_insert_rowid() "
        )
        comment_info = cur.fetchone()
        # Example response
        # {
        #   "commentid": 8,
        #   "lognameOwnsThis": true,
        #   "owner": "awdeorio",
        #   "ownerShowUrl": "/users/awdeorio/",
        #   "text": "Comment sent from httpie",
        #   "url": "/api/v1/comments/8/"
        # }
        #

        context = {
            "commentid": int(comment_info["commentid"]),
            "lognameOwnsThis": logname == comment_info["owner"],
            "owner": comment_info["owner"],
            "ownerShowUrl": "/users/" + str(comment_info["owner"]),
            "text": comment_info["text"],
            "url": f"/api/v1/comments/{comment_info['commentid']}/",
        }
        return flask.jsonify(**context), 201
    return flask.Response(status=404)


# Deals with deleting a comment
@skechy.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete comment."""
    connection = skechy.model.get_db()
    logname = login(connection)
    if not isinstance(logname, str):
        return flask.jsonify(**logname), 403

    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid=?", (commentid,)
    )
    comm_info = cur.fetchone()

    if comm_info is None:
        # commentid does not exist
        return flask.Response(status=404)

    if comm_info["owner"] != logname:
        # Logged in user does not own the like
        return flask.Response(status=403)

    connection.execute("DELETE FROM comments WHERE commentid=?", (commentid,))
    # Comment successfully deleted
    return flask.Response(status=204)
