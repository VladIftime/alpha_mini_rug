from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import follow_face


@inlineCallbacks
def behavior(session):
    yield follow_face(session)
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
    realm="rie.66d1bf9cafe50d23b76c4feb",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
