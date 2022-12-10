node parent_node {
}

node dialogue_root:parent_node {

}

node trivia_prompt:parent_node {
    has prompt;
    has answer;
    can select_trivia {
        //generate question
        num_trivia = 20;
        trivia_list = file.load_json("artTrivia2.json");
        trivia_seed = rand.integer(0, num_trivia - 1);
        trivia_pair = trivia_list["Trivia Pairs"][trivia_seed];
        

        //ask question
        prompt = trivia_pair[0];
        answer = trivia_pair[1];
    }
}

node trivia_response:parent_node {
    has output;
    can check_answer {
        if (visitor.response == visitor.answer) {
            output = ("Correct!\nWould you like another trivia question, or can I help you with something else?\n(Please input 'More trivia or Quit')");
            visitor.trivia_score += 1;
        } else {
            //output = ("Incorrect!\nWould you like another trivia question, or can I help you with something else?\n(Please input 'More trivia or Quit')");
            output = ("Sorry, the correct answer was: " + visitor.answer + ".\n Would you like another trivia question, or can I help you with something else?\n(Please input 'More trivia or Quit')");
            visitor.trivia_score = 0;
        }
    }

}
node trivia_decision:parent_node {}

node nearby_museums:parent_node {}

node dialogue_flow:parent_node {}

node collection_prompt:parent_node {}

node collection_response:parent_node {}

node collection_decision:parent_node {}

edge intent_transition {
    has intent;
}




graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;

        trivia_prompt = spawn node::trivia_prompt;
        trivia_response = spawn node::trivia_response;
        nearby_museums = spawn node::nearby_museums;
        dialogue_flow = spawn node::dialogue_flow;
        trivia_decision = spawn node::trivia_decision;
        update_history = spawn node::update_history;
        collection_prompt = spawn node::collection_prompt;
        collection_response = spawn node::collection_response;
        collection_decision = spawn node::collection_decision;

        // dialogue_root -[intent_transition(intent="trivia")]-> trivia_prompt;
        // dialogue_root -[intent_transition(intent="nearby museums")]-> nearby_museums;

        dialogue_root --> trivia_prompt;
        dialogue_root --> nearby_museums;
        dialogue_root --> dialogue_flow;
        dialogue_root --> collection_prompt;

        trivia_prompt --> trivia_response;
        trivia_response --> trivia_decision;
        trivia_decision --> dialogue_root;
        trivia_decision --> trivia_prompt;

        collection_prompt --> collection_response;
        collection_response --> collection_decision;
        collection_decision --> dialogue_root;
        collection_decision --> collection_prompt;
        
        nearby_museums --> dialogue_root;
        
        
        dialogue_flow --> dialogue_root;


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
    has response;
    has answer;
    has wlk_ctx = {};
    has trivia_score = 0;
    
    //can bi_end.infer;
    root {
        std.out("At root");
        //question = std.input("How can I assist you today? > ");
        take -->;
    }

    dialogue_root {
        std.out("At dialogue root");
        //take -->;

        if (response == "") {
            starter_dialogue = "Hello! How can I help you today?";
            yield report {"node":"dialogue_root", "nlg":starter_dialogue};
        } else {

        }
        

        if (response == "Play trivia") {
            std.out("Going to trivia!");
            take --> node::trivia_prompt;
        } elif (response == "Search nearby museums") {
            std.out("Goint to museums!");
            take --> node::nearby_museums;
        } elif (response == "Add to favorites") {
            std.out("Goint to favorites!");
            take --> node::collection_prompt;
        } else {
            std.out("Error choosing direction");
        }

        //take --> node::trivia_prompt;

        // intent_labels = -[intent_transition]->.edge.intent;
        // predicted_intent = bi_enc.infer(
        //     contexts = [response],
        //     candidates = intent_labels,
        //     context_type = "text",
        //     candidate_type = "text"
        // )[0]["predicted"]["label"];
        // take -[intent_transition(intent==predicted_intent)]-> node::parent_node;
    }
    
    trivia_prompt {
        std.out("At trivia prompt");
        here::select_trivia;
        answer = here.answer;
        yield report {"node":"trivia_prompt", "nlg":here.prompt};
        take --> node::trivia_response;
    }

    trivia_response {
        std.out("At trivia response");
        here::check_answer;
        yield report {"node":"trivia_response", "nlg":here.output, "score":trivia_score};
        take --> node::trivia_decision;
    }  

    trivia_decision {
        std.out("At trivia decision");
        if response == "More trivia" {
            std.out("Going to trivia prompt!");
            take --> node::trivia_prompt;
        } 
        else {
            std.out("Going to dialogue root");
            response = "";
            take --> node::dialogue_root;
        }
    }
    

    
    nearby_museums {
        std.out("At trivia decision");
        output = {"node":"nearby_museums", "nlg":""};
        yield report output;

        response = "";

        take --> node::dialogue_root;
    }

    dialogue_flow {
        output = {"node": "dialogue_flow", "nlg":""};

        yield report output;

        take --> node::dialogue_root;
    }

    collection_prompt {
        output = {"node": "collection_prompt", "nlg":"What would you like to add to your personal collection?"};

        yield report output;

        take --> node::collection_response;
    }

    collection_response {
        output = {"node": "collection_response", "data": response};
        yield report output;

        take --> node::collection_decision;

    }

    collection_decision {
        if response == "Add more to collection" {
            std.out("Going to collection probmpt!");
            take --> node::collection_prompt;
        } 
        else {
            std.out("Going to dialogue root");
            response = "";
            take --> node::dialogue_root;
        }
    }
}


