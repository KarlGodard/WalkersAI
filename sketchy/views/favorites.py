"""Favorites page."""
import flask
import sketchy
import pymongo
import bcrypt
import certifi
import json

# Adds Favorites page to website
@sketchy.app.route('/favorites/')
def favorites():
    if "username" in flask.session:
        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users

        username = flask.session["username"]
        user_found = records.find_one({"username": username})

        favorites = user_found["favorites"]
        return flask.render_template("favorites.html", favorites=favorites)
    else: # User is not logged in; don't return favorites list
        return flask.render_template("favorites.html")

# Adds Chat page to website
# If POST request, adds the request painting to the user favorites
@sketchy.app.route('/chat/', methods=["GET", "POST"])
def chat():
    message = ''
    if flask.request.method == "GET":
        return flask.render_template("chat.html")
    if flask.request.method == "POST" and "username" in flask.session:

        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users

        print(flask.request.get_json())
        print(flask.request.get_data())
        new_favorite = flask.request.get_json()["new_favorite"]
        print(new_favorite)
        username = flask.session["username"]
        user_found = records.find_one_and_update(
            { "username": username},
            {'$push': {"favorites": new_favorite}}

            )

        #user_found["favorites"].append(new_favorite)
        #print(user_found["favorites"])
        message = "Favorite has been added!"
        #return flask.render_template(None, message=message)
        status = {"message": message}
        return json.dumps(status)
    else:
        message = "Please sign in to save favorites!"
        status = {"message": message}
        return json.dumps(status)
        

        
