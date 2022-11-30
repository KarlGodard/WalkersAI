"""
Insta485 index (main) view.

URLs include:
/
"""
# import os
import flask
import sketchy
from serpapi import GoogleSearch

serpapi_key = "24f09a125c045af29485bcb5e2c2bcea6aa4ce1bb8a5590407438d9fdcf8789e"

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
    print(req)
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
        "WHERE lower(aw.title) = lower(?)",
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
        "WHERE lower(ai.displayName) = lower(?)",
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
        "WHERE lower(aw.title) = lower(?)",
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
        "WHERE lower(aw.title) = lower(?)",
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
        "WHERE lower(aw.title) = lower(?)",
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
        "WHERE lower(ai.displayName) = lower(?)",
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
        "WHERE lower(ai.displayName) = lower(?)",
        (artist_name,)
        )
        item = cur.fetchone()
        fulfillmentText = artist_name + " stopped his career in " + str(item['endDate'])
    if query_result.get('action') == 'get.identifyArt':
        question = query_results.get('queryText')
        fulfillmentText = identify_art_from_desc(question)
    return {
            "fulfillmentText": fulfillmentText,
            "source": "webhookdata"
        }

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
            answer = answer_box["title"]
            try:
                return answer_box["title"][:answer.index(" - Wikipedia")]
            except ValueError:
                return answer_box["title"]

    elif "knowledge_graph" in results.keys():
        art_list = []
        for key in results["knowledge_graph"].keys():
            for artwork in results["knowledge_graph"][key][:4]:
                art_list.append(artwork["name"] + " (by " + artwork["extensions"][0] + ")")
        output = "Here are some artworks matching that description: "
        for line in art_list[:-1]:
            output += line + ", "
        output += "and " + art_list[-1] + "."
        return output
    else:
        return "I couldn't find any specific paintings matching that description."



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

# Adds History page to website
@sketchy.app.route('/layout/')
def layout():
    return flask.render_template("layout.html")
    
# Adds History page to website
@sketchy.app.route('/history/')
def history():
    return flask.render_template("history.html")

    # Adds History page to website
@sketchy.app.route('/trivia/')
def trivia():
    return flask.render_template("trivia.html")