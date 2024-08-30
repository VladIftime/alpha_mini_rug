from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import follow_face


@inlineCallbacks
def behavior(session):
    yield follow_face(session)
    
    yield session.call("rie.dialogue.say", text="Red")
    yield session.call("rie.dialogue.say", text="Blue")
    yield session.call("rie.dialogue.say", text="yellow")
    yield session.call("rie.dialogue.say", text="red")
    yield session.call("rie.dialogue.say", text="purple")
    yield session.call("rie.dialogue.say", text="pink")
    yield session.call("rie.dialogue.say", text="Blue")
    yield session.call("rie.dialogue.say", text="Blue")
    yield session.call("rie.dialogue.say", text="Blue")
    yield session.call("rie.dialogue.say", text="Blue")
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
