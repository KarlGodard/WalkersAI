"""
Insta485 index (main) view.

URLs include:
/users/<user_url_slug>
"""

import flask
import sketchy
import pymongo
import json
import certifi


# Adds Chat page to website
# If POST request, adds the request painting to the user favorites
@sketchy.app.route('/trivia/', methods=["POST"])
def trivia_score():
    if "username" in flask.session:

        # These three lines should be temporary; will find global way to connect to database
        client = pymongo.MongoClient("mongodb+srv://clilian:ThisIsSketchy@sketchy-db.qgiklcy.mongodb.net/test", tlsCAFile=certifi.where())
        db = client.sketchy
        records = db.users

        username = flask.session["username"]
        user_found = records.find_one({"username": username})
        old_score = user_found["trivia_best"]
        new_score = flask.request.get_json()["score"]

        print(new_score)

        if int(new_score) > int(old_score):
            user_found = records.find_one_and_update(
                { "username": username},
                {'$set': {"trivia_best": new_score}}

                )
            message = "New high score!"
            status = {'message': message}
            return json.dumps(status)
        else:
            message = "No new high score."
            status = {'message': message}
            return json.dumps(status)


    else:
        message = "Please sign in to track your score!"
        status = {"message": message}
        return json.dumps(status)
        
