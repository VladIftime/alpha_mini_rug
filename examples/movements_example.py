from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import perform_movement


@inlineCallbacks
def main(session, details):
    frames = [
        {"time": 800, "data": { "body.arms.right.upper.pitch": -1.7,"body.arms.left.upper.pitch": -1.7},},
        {"time": 1600, "data": {"body.arms.right.upper.pitch": 0.5,"body.arms.left.upper.pitch": 0.5},},
    ]
    
    yield perform_movement(session=session, frames=frames, force=True)

    session.leave()


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
