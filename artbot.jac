node parent_node {
    can bi_enc.infer;

    can classify_intent {
        #TODO: update implementation
        # Default to user asking about a painting
        intent_labels = ["trivia", "nearby", "MoMa", 
        "Save Image", "Painting Exploration"];
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

node dialogue_root:parent_node {
    can nlu {
        //::classify_intent;
    }
    can process {
       // visitor.wlk_ctx["next_state"] = (-[intent_transition(intent==visitor.wlk_ctx["intent"])]->)[0];
        //visitor.wlk_ctx["next_state"] = 
    }
    can nlg {
        //visitor.response = "Sorry I can't handle that just yet. Anything else I can help you with?";
    }
}



node trivia_node:parent_node {
    can conduct_trivia {
        //generate question
        num_trivia = 20;
        trivia_list = file.load_json("artTrivia2.json");
        trivia_seed = rand.integer(0, num_trivia);
        std.out(trivia_list);
        trivia_pair = trivia_list["Trivia Pairs"][trivia_seed];
        

        //ask question
        prompt = trivia_pair[0];
        std.out(prompt);


        //get response
        response = std.input("Response > ");

        //check response
        if (response == trivia_pair[1]) {
            std.out("Correct!\n");
        } else {
            std.out("Sorry, the correct answer was: ");
            std.out(trivia_pair[1]);
            std.out("\n");
        }


        //ask qbout what to do next
        std.out("Would you like another trivia question, or can I help you with something else?\n");

        next_move = std.input("> ");
    }
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
        ::classify_intent;
        ::extract_entity;
    }
    can process {
        data = file.load_json("painting1.json");
        std.out(data);
        queried_data = data[visitor.wlk_ctx["intent"]];
        visitor.wlk_ctx["respond"] = true;
        visitor.wlk_ctx["response"] = queried_data;
    }
    can nlg {
        visitor.response = visitor.wlk_ctx["response"];
    }
}


node query_database_node:parent_node {
    has name = "Query Database";
    can nlu {
        ::classify_intent;
    }
    can process {
        data = file.load_json("painting1.json");
        std.out(data);
        queried_data = data[visitor.wlk_ctx["intent"]];
        visitor.wlk_ctx["respond"] = true;
        visitor.wlk_ctx["response"] = queried_data;
    }
    can nlg {
        visitor.response = visitor.wlk_ctx["response"];
    }
}

graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;
        trivia_prompt = spawn node::trivia_prompt;
        trivia_response = spawn node::trivia_response;
        trivia_node = spawn node::trivia_node;
        select_painting = spawn node::select_painting_node;
        query_database = spawn node::query_database_node;

        select_painting --> query_database;
        select_painting --> select_painting;
        query_database --> query_database;
        query_database --> select_painting;
        dialogue_root --> trivia_node;
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
    can bi_enc.infer;
    has wlk_ctx = {};
    has response;
    root {
        
        question = std.input("How can I assist you today? > ");
        take -->;
    }

    dialogue_root {
        take -->;

        
        // if (!question) {
        //     question = std.input("How can I assist you today? > ");
        //     here::init_wlk_ctx;
        // }
        // here::nlu;
        // here::process;
        // here::nlg;
        // std.out(response);
        // question = null;
        // take visitor.wlk_ctx["next_state"] else: take here;
        
    }

    trivia_node {
        here::conduct_trivia;
    }
    trivia_prompt {
        here::process;
        here::nlg;
        std.out(response);
        question = null;
        take -->;
    }

    trivia_response {
        here::nlu;
        here::process;
        here::nlg;
        std.out(response);
        question = null;
        take visitor.wlk_ctx["next_state"] else: take here;
    }

    select_painting_node {
        #steps:
        #. 0) Prompt user to ask about painting
        #  1) Receives user's answer
        #  2) Processes which painting user refers to
        #  3) Pass information t

        
        question = std.input("Question (Ctrl-C to exit)> ");
        here::init_wlk_ctx;
        
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

    query_database_node {
        if (!question) {
             question = std.input("Question (Ctrl-C to exit)> ");
        }

        here::nlu;
        here::process;
        here::nlg;
        std.out(response);
        question = null;

        #logic for determining the next node
        # If user wants to continue asking about current painting (stay on node)
        if (visitor.wlk_ctx["respond"]) {
            here::nlg;
            std.out(response);
            question = null;
            take here;
        } 
        else { 
            # If user wants to ask about new painting (back to select_painting)
            take visitor.wlk_ctx["next_state"] else: take here;
        }
        

    }
}