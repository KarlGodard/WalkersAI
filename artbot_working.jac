node parent_node {
    has name;
    can bi_enc.infer;
    can tfm_ner.extract_entity;

    can classify_intent {
        #TODO: update implementation
        # Default to user asking about a painting
        intent_labels = -[intent-transition]->.edge.intent;
        visitor.wlk_ctx["intent"] = bi_enc.infer(
            contexts = [visitor.question],
            candidates = intent_labels,
            context_type = "text",
            candidate_type = "text"
        )[0]["predicted"]["label"];
        std.out(visitor.wlk_ctx["intent"]);
    }

    can extract_entity {
        #TODO: update implementation
        # Get name of painting
        res = tfm_ner.extract_entity(visitor.question);
        for ent in res {
            ent_type = ent["entity_value"];
            ent_text = ent["entity_text"];
            if (!(ent_type in visitor.wlk_ctx["entities"])){
                visitor.wlk_ctx["entities"][ent_type] = [];
            }
            visitor.wlk_ctx["entities"][ent_type].l::append(ent_text);
        }
    }

    can init_wlk_ctx {
        new_wlk_ctx = {
            "intent": null,
            "entities": {},
            "prev_state": null,
            "next_state": null,
            "respond": false,
            "response": null
        };

        visitor.wlk_ctx = new_wlk_ctx;
    }
    can nlu {}
    can process {}
    can nlg {}
}

node select_painting_node:parent_node {
    has name = "Select Painting";
    can init_wlk_ctx {
        new_wlk_ctx = {
            "intent": null,
            "entities": {},
            "prev_state": null,
            "next_state": null,
            "respond": false,
            "response": null
        };

        visitor.wlk_ctx = new_wlk_ctx;
    }

    can nlu {
        if (!visitor.wlk_ctx["intent"]): ::classify_intent;
        ::extract_entity;
    }
    can process {
        # Copied from walkthrough, will verify for correctness

        # Required: topic (current painting), query (current question)
        required_entities = ["topic", "query"];
        if (vector.sort_by_key(visitor.wlk_ctx["entities"].d::keys) == vector.sort_by_key(required_entities)) {
            visitor.wlk_ctx["next_state"] = -[entity_transition]->[0];
            visitor.wlk_ctx["prev_state"] = here;
        } elif (visitor.wlk_ctx["prev_state"] and !visitor.wlk_ctx["prev_state"].context["name"] in ["test_drive", "td_confirmation"]){
            next_state = -[intent_transition(intent==visitor.wlk_ctx["intent"])]->;
            if (next_state.length > 0 and visitor.wlk_ctx["intent"] != "no") {
                visitor.wlk_ctx["next_state"] = next_state[0];
                visitor.wlk_ctx["prev_state"] = here;
            } else {
                visitor.wlk_ctx["respond"] = true;
            }
        } else {
            visitor.wlk_ctx["respond"] = true;
        }
    }
    can nlg {
        visitor.response = "Please ask a question about a painting.";
    }
}


node query_database_node:parent_node {
    has name = "Query Database";
    can nlu {
        if (!visitor.wlk_ctx["intent"]): ::classify_intent;
    }
    can process {
        required_entities = -[entity_transition]->.edge[0].context["entities"];

        data = file.load_json("painting1.json");
        std.out(data);
        queried_data = data[visitor.wlk_ctx["intent"]];

        # Uses "query" and "topic" to get answer
        visitor.wlk_ctx["respond"] = true;
        visitor.wlk_ctx["response"]["answer"] = queried_data;
    }
    can nlg {
        # visitor.response = visitor.wlk_ctx["response"];
        # Entities are from select_painting node
        # This response is just for testing the entity extraction
        visitor.response = "You asked about " + visitor.wlk_ctx["entities"]["topic"][0] + " and want to know the " + visitor.wlk_ctx["entities"]["query"][0];
    }
}

edge intent_transition {
    has intent;
}

graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;
        select_painting = spawn node::select_painting_node;
        query_database = spawn node::query_database_node;

        # "topic" indicates current painting user is discussing
        # "query" indicates the question user is currently asking
        dialogue_root -[intent_transition(intent="select_painting")]-> select_painting;

        select_painting -[intent_transition(entities=["query"])]-> query_database;
        # select_painting --> select_painting;
        query_database -[intent_transition(entities=["query"])]-> query_database;
        query_database -[intent_transition(intent="end current query")]-> select_painting;
    }
}

walker init {
    root {
        spawn here --> graph::dialogue_system;
        spawn here walker::bot;
    }
}

walker bot {
    has question;
    # can bi_enc.infer;
    has wlk_ctx = {};
    has response;
    root {
        take --> node::dialogue_root;
    }

    parent_node {
        #steps:
        #. 0) Prompt user to ask about painting
        #  1) Receives user's answer
        #  2) Processes which painting user refers to
        #  3) Pass information to next node

        # Added back this conditional bc this should only show up at 
        # beginning of dialogue (other prompts for other stages)
        if (!question) {
            question = std.input("Question (Ctrl-C to exit)> ");
            here::init_wlk_ctx;
        }
        
        here::nlu;
        here::process;
        if (visitor.wlk_ctx["respond"]) {
            here::nlg;
            std.out(response);
            question = null;
            take here;
        } else {
            take visitor.wlk_ctx["next_state"] else: take here;
        }
    }

# Not needed because select_painting_node and query_database_node both inherit from parent_node

    #query_database_node {
    #    has question;
    #    if (!question) {
    #        question = std.input("Question (Ctrl-C to exit)> ");
    #    }

    #    here::nlu;
    #    here::process;
    #    here::nlg;
    #    std.out(response);
    #    question = null;
    #
    #    #logic for determining the next node
    #    # If user wants to continue asking about current painting (stay on node)
    #    if (visitor.wlk_ctx["respond"]) {
    #        here::nlg;
    #        std.out(response);
    #        question = null;
    #        take here;
    #    } 
    #    else { 
    #        # If user wants to ask about new painting (back to select_painting)
    #        take visitor.wlk_ctx["next_state"] else: take here;
    #    }
    #}

}