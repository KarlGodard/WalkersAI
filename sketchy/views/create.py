"""
Insta485 create account view.

URLs include:
/accounts/create/
"""
import hashlib
import os
import uuid
import pathlib
import flask
import sketchy


@sketchy.app.route("/accounts/create/", methods=["POST", "GET"])
def show_create():
    """Generate create page."""
    # If user is logged in, redirect to /accounts/edit/
    if "username" in flask.session:
        return flask.redirect("/accounts/edit/")
    return flask.render_template("create.html")


# Handles account creation, deletion, and login


@sketchy.app.route("/accounts/", methods=["POST"])
def handle_account_ops():
    """Handle account operation."""
    # if flask.request.method == "POST" and 'username' not in flask.session:
    # flask.abort(403)
    filename = flask.request.args.get("target")
    if filename is None:
        filename = flask.url_for("show_index")
        # return flask.redirect(flask.url_for("show_index"))

    connection = sketchy.model.get_db()
    if flask.request.form["operation"] == "update_password":
        update_password(connection)
    elif flask.request.form["operation"] == "delete":
        filename = flask.request.args["target"]

        # Check user logged in
        if "username" not in flask.session:
            flask.abort(403)

        logname = flask.session["username"]

        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (logname,)
        )
        files = cur.fetchall()
        for file in files:
            file_path = os.path.join(
                sketchy.app.config["UPLOAD_FOLDER"], file["filename"]
            )
            os.remove(file_path)

        cur = connection.execute(
            "SELECT filename FROM posts " "WHERE owner=?", (logname,)
        )
        files = cur.fetchall()

        for file in files:
            file_path = os.path.join(
                sketchy.app.config["UPLOAD_FOLDER"], file["filename"]
            )
            os.remove(file_path)

        connection.execute("DELETE FROM users " "WHERE username=?", (logname,))
        flask.session.clear()
        return flask.redirect(filename)
    elif flask.request.form["operation"] == "edit_account":
        # Check if user logged in
        if "username" not in flask.session:
            flask.abort(403)

        abort400 = "fullname" not in flask.request.form
        abort400 = abort400 or "email" not in flask.request.form
        if abort400:
            flask.abort(400)

        logname = flask.session["username"]

        update_info(connection, logname)
        return flask.redirect(filename)

    if flask.request.form["operation"] == "login":
        connection = login()
        return flask.redirect(filename)

    if flask.request.form["operation"] == "create":
        create(connection)

    # elif flask.request.form['operation'] == 'login':
    if filename is None:
        return flask.redirect("/")
    return flask.redirect(filename)


def update_info(connection, logname):
    """Update info of a user."""
    # If no picture is included, only edit username and email
    if flask.request.files["file"].filename == "":
        connection.execute(
            "UPDATE users SET fullname=?, email=? WHERE username=?",
            (
                flask.request.form["fullname"],
                flask.request.form["email"],
                logname,
            ),
        )
    else:
        update_with_picture(connection, logname)


def login():
    """Handle login operation."""
    abort400 = "username" not in flask.request.form
    abort400 = abort400 or "password" not in flask.request.form
    algorithm = "sha512"
    if abort400:
        flask.abort(400)
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    connection = sketchy.model.get_db()

    cur = connection.execute(
        "SELECT password " "FROM users " "WHERE username = ?",
        (username,),
    )
    curr_password = cur.fetchone()

    salt = curr_password["password"].split("$")[1]
    print(salt)

    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    cur = connection.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ? AND password = ?",
        (
            username,
            password_db_string,
        ),
    )
    result = cur.fetchone()
    if result is None:
        flask.abort(403)
    flask.session["username"] = username
    return connection


def create(connection):
    """Create new user."""
    # Abort 400 if any inputs are empty
    for form in flask.request.form:
        if form is None:
            flask.abort(400)

    if "file" not in flask.request.files:
        flask.abort(400)
        # Check if username is taken
    cur = connection.execute(
        "SELECT username FROM users WHERE username=?",
        (flask.request.form["username"],),
    )
    # Abort(409) if the username is taken
    if len(cur.fetchall()) != 0:
        flask.abort(409)

    salt = uuid.uuid4().hex

    hash_obj = hashlib.new("sha512")
    password_salted = salt + flask.request.form["password"]
    hash_obj.update(password_salted.encode("utf-8"))
    password_db_string = "$".join(["sha512", salt, hash_obj.hexdigest()])

    file = flask.request.files["file"]
    path = pathlib.Path(file.filename).suffix
    uuid_basename = f"{uuid.uuid4().hex}{path}"
    # Save to disk
    file.save(sketchy.app.config["UPLOAD_FOLDER"] / uuid_basename)
    cur = connection.execute(
        "INSERT INTO users(username, fullname, "
        " email, filename, password) "
        "VALUES(?, ?, ?, ?, ?)",
        (
            flask.request.form["username"],
            flask.request.form["fullname"],
            flask.request.form["email"],
            uuid_basename,
            password_db_string,
        ),
    )
    flask.session["username"] = flask.request.form["username"]


def update_with_picture(connection, logname):
    """Update user info with picture."""
    # Unpack flask object
    fileobj = flask.request.files["file"]
    filename1 = fileobj.filename
    # Compute base name (filename without directory).
    # We use a UUID to avoid
    # clashes with existing files, and ensure that the
    # name is compatible with the
    # filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename1).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = sketchy.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    connection.execute(
        "UPDATE users SET filename=?, fullname=?, " "email=? WHERE username=?",
        (
            uuid_basename,
            flask.request.form["fullname"],
            flask.request.form["email"],
            logname,
        ),
    )


def update_password(connection):
    """Update the user's password."""
    if "username" not in flask.session:
        flask.abort(403)
    logname = flask.session["username"]
    cur = connection.execute(
        "SELECT username, password FROM users WHERE username=? ", (logname,)
    )
    user = cur.fetchone()
    password0 = flask.request.form["password"]
    password1 = flask.request.form["new_password1"]
    password2 = flask.request.form["new_password2"]

    salt = user["password"].split("$")[1]

    algorithm = "sha512"
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password0
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if password1 == password2 and user["password"] == password_db_string:
        algorithm = "sha512"
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password1
        hash_obj.update(password_salted.encode("utf-8"))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        cur = connection.execute(
            "UPDATE users SET password =? WHERE username=? ",
            (password_db_string, logname),
        )
