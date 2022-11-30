node parent_node {
}

node dialogue_root:parent_node {

}



node trivia_node:parent_node {
    can conduct_trivia {
        //generate question
        num_trivia = 20;
        trivia_list = file.load_json("artTrivia2.json");
        trivia_seed = rand.integer(0, num_trivia);
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
        }


        //ask qbout what to do next
        std.out("Would you like another trivia question, or can I help you with something else?\n");

        next_move = std.input("> ");
    }
}



graph dialogue_system {
    has anchor dialogue_root;
    spawn {
        dialogue_root = spawn node::dialogue_root;
        trivia_node = spawn node::trivia_node;
    
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
    has wlk_ctx = {};
    has response;
    root {
        //question = std.input("How can I assist you today? > ");
        take -->;
    }

    dialogue_root {
        take -->;
    }

    trivia_node {
        here::conduct_trivia;
    }
    
}

