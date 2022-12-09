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
import requests
import json

serpapi_key = "e2f1eb7309c17ffc3443c9780ce1c250daf898f28fa1658ebd7c74556b629bfd"
API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": f"Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

@sketchy.app.route("/")
def show_index():
    
    context = {"logname": "Nate"}
    
    return flask.render_template("home.html", **context)

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

@sketchy.app.route("/nearbyMuseums/", methods=["GET"])
def nearbyMuseums():
   
    payload={}
    headers = {}

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=42.279545,-83.741063&radius=1500&type=museum&key=AIzaSyCAT9OGOYQL6zPlTgc73N_MB1fDC-sXFks"

    response = requests.request("GET", url, headers=headers, data=payload)
    print(type(response))
    print(type(response.json()))
    print(response.json())
    #results = json.loads(response.text)['results']

    # for result in results:
    #    print(result['name'])

    return response.json()