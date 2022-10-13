node dialogue_state {
    can bi_enc.infer;

    can classify_intent {
        intent_labels = -[intent_transition]->.edge.intent;
        visitor.wlk_ctx["intent"] = bi_enc.infer(
            contexts = [visitor.question],
            candidates = intent_labels,
            context_type = "text",
            candidate_type = "text"
        )[0]["predicted"]["label"];
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

node dialogue_root:dialogue_state {
    has name = "only_node";
    can nlu {
        ::classify_intent;
    }
    can process {
        data = file.load_json("painting1.json");
        queried_data = data[visitor.walk_ctx["intent"]];
        visitor.wlk_ctx["respond"] = true;
        visitor.walk_ctx["response"] = queried_data;
    }
    can nlg {
        visitor.response = visitor.walk_ctx["response"];
    }
}

graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;
    }
}

walker init {
    root {
        spawn here --> graph::dialogue_system;
        spawn here walker::talk;
    }
}



walker talk {
    has question;
    has wlk_ctx = {};
    has response;
    root {
        take --> node::dialogue_root;
    }
    dialogue_state {
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
}