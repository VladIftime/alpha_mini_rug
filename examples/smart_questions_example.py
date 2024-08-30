from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import smart_questions


@inlineCallbacks
def behavior(session):
    question_test = "What is the capital of Netherlands?"
    answers = {"amsterdam": ["amster", "dam", "amsterdam", "amsterd"]}

    answer = yield smart_questions(
        session, question=question_test, answer_dictionary=answers, debug=True
    )

    print(answer)

    session.leave()

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
