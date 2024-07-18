from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.util import sleep
from alpha_mini_rug import aruco_detect_markers


@inlineCallbacks
def main(session, details):
    print("Hello, world!")
    yield session.subscribe(aruco_detect_markers, "rom.sensor.sight.stream")
    yield session.call(
        "rom.sensor.sight.sensitivity"
    )  # Set the sensitivity of the camera and call the stream
    yield session.call("rom.sensor.sight.stream")
    print("Subscribed to the camera stream")


wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.6690edeee1b5df3bc1d36816",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
