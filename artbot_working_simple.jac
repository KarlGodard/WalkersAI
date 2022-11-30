node faq_root;
node faq_state {
    has question;
    has answer;
}

// Static graph definition
graph faq {
    has anchor faq_root;
    spawn {
        // Spawning the nodes
        faq_root = spawn node::faq_root;
        faq_answer_1 = spawn node::faq_state(
            question="Who painted The Starry Night?",
            answer="Vincent van Gogh painted Starry Night."
        );
        faq_answer_2 = spawn node::faq_state(
            question="When was Starry Night painted?",
            answer="Stary Night was painted in June 1889."
        );
        faq_answer_3 = spawn node::faq_state(
            question="How was Starry Night painted?",
            answer="The medium is oil on canvas."
        );

        // Connecting the nodes together
        faq_root --> faq_answer_1;
        faq_root --> faq_answer_2;
        faq_root --> faq_answer_3;
    }
}

walker init {
    root {
        spawn here --> graph::faq;
        spawn here walker::ask;
    }
}

walker ask {
    can use.qa_classify;
    has question;
    root {
        question = std.input("> ");
        take --> node::faq_root;
    }
    faq_root {
        answers = -->.answer;
        best_answer = use.qa_classify(
            text = question,
            classes = answers
        );
        take --> node::faq_state(answer==best_answer["match"]);
    }
    faq_state {:
        std.out(here.answer);
    }
}