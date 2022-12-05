"""
Insta485 index (main) view.

URLs include:
/
"""
# import os
import flask
import sketchy
import requests
import wikipedia
from serpapi import GoogleSearch

serpapi_key = "51e0ce06fdd21377cd353feb0dd6e9549d0f975fe682b149f2955fb5d3c47abe"
API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": f"Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

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

specific_artist = ''
specific_artwork = ''
content = ''
text = ''
question = ''
@sketchy.app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    connection = sketchy.model.get_db()
    req = flask.request.get_json(silent=True, force=True)
    print(req)
    fulfillmentText = ''
    fulfillment = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
    }
    reply = fulfillment
    
    query_result = req.get('queryResult')
    global content
    global specific_artist
    global specific_artwork
    global text
    global question
    #print(content)
    # Store new Artist
    #print(query_result.get('action'))
    if query_result.get('action') == 'get.summary':
        specific_artist = query_result.get('parameters')['name']
        specific_artwork = query_result.get('parameters')['name']
        content = content = wikipedia.page(query_result.get('parameters')['name']).content
        fulfillmentText = wikipedia.summary(query_result.get('parameters')['name'], sentences=4)
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.newArtist':
        specific_artist = query_result.get('parameters')['person']['name']
        print(specific_artist)
        content = wikipedia.page(specific_artist).content
        print(wikipedia.summary(specific_artist))
        reply = fulfillment
    # Store new Artwork
    if query_result.get('action') == 'get.newArtwork':
        specific_artwork = query_result.get('parameters')['painting']
        print(specific_artwork)
        #print(specific_artwork)
        content = wikipedia.page(specific_artwork).content
        print(wikipedia.summary(specific_artwork, sentences=4))
        reply = fulfillment
    # Gets new Artwork Question
    if query_result.get('action') == 'get.newQuestion':
        #print(query_result.get('queryText'))
        print('first1')
        question = query_result.get('queryText')
        print(question)
        reply = {
        "followupEventInput": {
        "name": "extend_webhook_deadline",
        "languageCode": "en-US"
        }
        }
        output = query({"inputs": {
		"question": question,
		"context": content},})
        print(output)
        text = output['answer']
        
        
    # Gets new Artist Question
    if query_result.get('action') == 'get.newArtistQuestion':
        #print(content)
        #print(query_result.get('queryText'))
        print('first2')
        question = query_result.get('queryText')
        output = query({"inputs": {
		"question": question,
		"context": content},})
        print(output)
        text = output['answer']
        fulfillmentText = text
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
        
    if query_result.get('action') == 'followupevent':
        print('first3')
        reply = {
        "followupEventInput": {
        "name": "extend_webhook_deadline_2",
        "languageCode": "en-US"
        }
        }

    if query_result.get('action') == 'followupevent2':
        fulfillmentText = text
        print(fulfillmentText)
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    # Starts database answers
    if query_result.get('action') == 'get.painter':
        ### Perform set of executable code
        ### if required
        ###
        parameters = query_result.get('parameters')
        painting_name = parameters['painting']
        print(painting_name)
        cur = connection.execute(
        "SELECT aw.constituentID "
        "FROM artworks aw "
        "WHERE lower(aw.title)= lower(?)",
        (painting_name,)
        )
        painter_name = cur.fetchone()
        painter_id = painter_name['constituentID']
        print('break')
        print(painter_id)
        cur = connection.execute(
        "SELECT ai.displayName "
        "FROM artists ai "
        "WHERE ai.constituentID= ?",
        (painter_id,)
        )
        painter_name = cur.fetchone()
        print(painter_name['displayName'])
        fulfillmentText = painter_name['displayName'] + " painted the " + painting_name
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.nationality':
        painter_name = query_result.get('parameters')['person']['name']
        cur = connection.execute(
        "SELECT ai.nationality "
        "FROM artists ai "
        "WHERE ai.displayName = ?",
        (painter_name,)
        )
        nationality = cur.fetchone()
        print(nationality)
        fulfillmentText = painter_name + " is " + nationality['nationality']
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.medium':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.medium "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE lower(aw.title) = lower(?)",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The medium of " + painting_name + " is a " + item['medium']
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.dimensions':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.dimensions "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE lower(aw.title) = lower(?)",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The " + painting_name + " has dimensions of " + item['dimensions']
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.yearPainted':
        painting_name = query_result.get('parameters')['painting']
        cur = connection.execute(
        "SELECT aw.date "
        "FROM artworks aw "
        "JOIN artists ai ON ai.constituentID = aw.constituentID "
        "WHERE lower(aw.title) = lower(?)",
        (painting_name,)
        )
        item = cur.fetchone()
        fulfillmentText = "The " + painting_name + " was painted in " + item['date']
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.beginDate':
        artist_name = query_result.get('parameters')['person']['name']
        print(artist_name)
        cur = connection.execute(
        "SELECT ai.beginDate "
        "FROM artists ai "
        "WHERE ai.displayName = ?",
        (artist_name,)
        )
        item = cur.fetchone()
        if not bool(item):
            fulfillmentText = artist_name + " wasn't found in database."
        else:
            fulfillmentText = artist_name + " was born in " + str(item['beginDate']) + "."
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.endDate':
        artist_name = query_result.get('parameters')['person']['name']
        cur = connection.execute(
        "SELECT ai.endDate "
        "FROM artists ai "
        "WHERE ai.displayName = ?",
        (artist_name,)
        )
        item = cur.fetchone()
        if not bool(item):
            fulfillmentText = artist_name + " wasn't found in database."
        else:
            if(item['endDate'] == 0):
                fulfillmentText = artist_name + " is still alive."
            else:
                fulfillmentText = artist_name + " died in " + str(item['endDate']) + "."
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    if query_result.get('action') == 'get.identifyArt':
        #print("hello")
        question = query_result.get('queryText')
        fulfillmentText = identify_art_from_desc(question)
        reply = {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }
    #print(reply)
    return reply
    

def identify_art_from_desc(question):
    params = {
        "q": question,
        "hl": "en",
        "gl": "us",
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "answer_box" in results.keys():
        answer_box = results["answer_box"]
        #Fix spelling error if one was detected
        if results["search_information"]["organic_results_state"] == "Showing results for exact spelling despite spelling suggestion":
            print("SPELLING ERROR. RETRYING")
            #Will not cause infinite loop unless Google's spelling correction stops working
            return identify_art_from_desc(results["search_information"]["spelling_fix"])
        
        if answer_box["type"] == 'organic_result':
            if "answer" in answer_box.keys():
                return answer_box["answer"]
            answer = answer_box["title"]
            try:
                return answer_box["title"][:answer.index(" - Wikipedia")]
            except ValueError:
                return answer_box["title"]

    elif "knowledge_graph" in results.keys():
        art_list = []
        for key in results["knowledge_graph"].keys():
            if "artworks" in key:
                for artwork in results["knowledge_graph"][key][:4]:
                    art_list.append(artwork["name"] + " (by " + artwork["extensions"][0] + ")")
        output = "Here are some artworks matching that description: "
        for line in art_list[:-1]:
            output += line + ", "
        output += "and " + art_list[-1] + "."
        return output
    else:
        return "I couldn't find any specific artwork matching that description."



@sketchy.app.route("/uploads/<filename>")
def upload_file(filename):
    """Upload file."""
    if 'username' not in flask.session:
        flask.abort(403)

    upload_folder = sketchy.app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(upload_folder, filename)

# Adds Home page to website
@sketchy.app.route('/index/')
def index():
    return flask.render_template("index.html")

# Adds Home page to website
@sketchy.app.route('/home/')
def home():
    return flask.render_template("home.html")

# Adds Search for painting page to website
@sketchy.app.route('/search/')
def search():
    return flask.render_template("search.html")

# Adds History page to website
@sketchy.app.route('/layout/')
def layout():
    return flask.render_template("layout.html")
    
# Adds History page to website
@sketchy.app.route('/history/')
def history():
    return flask.render_template("history.html")

    # Adds History page to website
@sketchy.app.route('/about/')
def about():
    return flask.render_template("about.html")