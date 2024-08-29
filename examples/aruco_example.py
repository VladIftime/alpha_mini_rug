from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import aruco_detect_markers


def aruco(frame):
    corners, ids = aruco_detect_markers(frame)
    print("corners:", corners)
    print("ids:", ids)
    pass


@inlineCallbacks
def behavior(session):
    yield session.subscribe(aruco, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
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
