"""Logging in and out."""
import flask
import sketchy
import pymongo
import bcrypt

@sketchy.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """Logout."""
    if flask.request.method == "POST" and 'username' not in flask.session:
       flask.abort(403)
    # POST-only route for handling logout requests
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))



# Login page
# If POST request, user is trying to login ==> check if username and password are right
# If GET request, user is just accessing page
@sketchy.app.route("/accounts/login/", methods=['post', 'get'])
def login():
    message = ''
    if "username" in flask.session:
        return flask.redirect(flask.url_for("user"))
    if flask.request.method == "POST":
        user = flask.request.form.get("username")
        
        password = flask.request.form.get("password")

        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test")
        db = client.sketchy
        records = db.users
        
        user_found = sketchy.records.find_one({"name": user})
        if user_found:
            user_val = user_found["name"]
            passwordcheck = user_found["password"]

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                flask.session["name"] = user_val
                return flask.redirect(flask.url_for('logged_in'))
            else:
                message = "Wrong password"
                return flask.render_template("login.html", message=message)
        else:
            message = "Email not found"
            return flask.render_template('login.html', message=message)
    return flask.render_template('login.html')


# Create account page
# If POST request, user is creating an account ==> check if username is taken
# If GET request, user is just accessing page
@sketchy.app.route("/accounts/create/", methods=['post', 'get'])
def create_account():
    message = ''
    if flask.request.method == "POST":
        user = flask.request.form.get("username")
        
        password = flask.request.form.get("password")

        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test")
        db = client.sketchy
        records = db.users
        
        user_found = records.find_one({"name": user})
        if user_found:
            message = 'There already is a user by that name'
            return flask.render_template('create.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'password': hashed}
            records.insert_one(user_input)
   
            return flask.render_template('user.html')
    return flask.render_template("create.html")

# Logged in page: if the user is already logged in
@sketchy.app.route('/user/')
def logged_in():
    if "name" in flask.session:
        name = flask.session["name"]
        return flask.render_template('user.html', name=name)
    else:
        return sketchy.redirect(flask.url_for("login.html"))
