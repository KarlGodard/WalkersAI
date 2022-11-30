node dialogue_root;

node dialogue_state {
    has name;
    has response;
}

node parent_node {
    has name;
    has response;
}

edge intent_transition {
    has intent;
}

graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;
        select_painting = spawn node::dialogue_state(
            name = "Select Painting",
            response = "What would you like to know about this painting?"
        );
        query_database = spawn node::dialogue_state(
            name = "Query Database",
            response = "Here's your fun fact about this painting."
        );

        dialogue_root -[intent_transition(intent="select painting")]-> select_painting;
        dialogue_root -[intent_transition(intent="make query")]-> query_database;
        select_painting -[intent_transition(intent="make query")]-> query_database;
        query_database -[intent_transition(intent="make query")]-> query_database;
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
    can bi_enc.infer;
    root {
        question = std.input("> ");
        take --> node::dialogue_root;
    }
    dialogue_root {
        intent_labels = -[intent_transition]->.edge.intent;
        predicted_intent = bi_enc.infer(
            contexts = [question],
            candidates = intent_labels,
            context_type = "text",
            candidate_type = "text"
        )[0]["predicted"]["label"];
        take -[intent_transition(intent==predicted_intent)]-> node::dialogue_state;
    }
    dialogue_state {
        std.out(here.response);
    }
}