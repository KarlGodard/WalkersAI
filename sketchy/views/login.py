"""Logging in and out."""
import flask
import sketchy
import pymongo
import bcrypt
import certifi
import random


# Logout page
# If user is logged in, redirects to telling user they have logged out
# If user was not logged in, redirects to login page
@sketchy.app.route('/accounts/logout/', methods=["POST", "GET"])
def logout():
    if "username" in flask.session:
        flask.session.pop("username", None)
        return flask.render_template("signout.html")
    else:
        return flask.render_template("login.html")


# Login page
# If POST request, user is trying to login ==> check if username and password are right
# If GET request, user is just accessing page
@sketchy.app.route("/accounts/login/", methods=['post', 'get'])
def login():
    message = ''
    if "username" in flask.session:
        return flask.render_template('user.html')
    if flask.request.method == "POST":
        user = flask.request.form.get("username")
        
        password = flask.request.form.get("password")

        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users
        
        user_found = records.find_one({"username": user})
        if user_found:
            user_val = user_found["username"]
            passwordcheck = user_found["password"]

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                flask.session["username"] = user_val
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
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users
        
        user_found = records.find_one({"username": user})
        if user_found:
            message = 'There already is a user by that name'
            return flask.render_template('create.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username': user, 'password': hashed, 'favorites':[]}
            records.insert_one(user_input)
   
            return flask.render_template('user.html', username=user)
    return flask.render_template("create.html")

# Logged in page: if the user is already logged in
@sketchy.app.route('/user/')
def logged_in():
    if "username" in flask.session:
        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users

        username = flask.session["username"]
        user_found = records.find_one({"username": username})

        print(user_found["favorites"])
        if len(user_found["favorites"]) > 0:
            random_painting = random.choice(user_found["favorites"])
            return flask.render_template('user.html', username=username, fav=random_painting)
        else:
            return flask.render_template('user.html', username=username, fav=None)
    else:
        return flask.redirect(flask.url_for("login"))
