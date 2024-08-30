from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import key_words


@inlineCallbacks
def behavior(session):
    # define question 1 together with the keywords and answers
    question_colors = "What is your favorite color?"
    keywords_colors = ["red", "blue", "green", "yellow", "pink", "orange", "purple"]

    # call keywords function, setting the language of both question and answer
    # to English; records the answer with a certainty higher than 0.1 for 5
    # seconds; with the debug flag set to true, it prints all the words heard
    answer = yield key_words(
        session,
        question=question_colors,
        question_lang="en",
        key_words=keywords_colors,
        key_words_lang="en",
        time=5,
        certainty=0.1,
        debug=True,
    )

    if answer is not None:
        string = "My favorite color is also " + answer
    else:
        string = "Didn't understand your answer, try again later"

    yield session.call("rie.dialogue.say", text=string)

    pass


def main(session, details):
    behavior(session)
    pass


wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.66cdbc1aafe50d23b76c2e6b",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
