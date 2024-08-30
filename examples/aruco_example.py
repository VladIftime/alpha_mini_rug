from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import aruco_detect_markers

ids_code = None


@inlineCallbacks
def aruco(session, frame):
    global ids_code
    corners, ids = aruco_detect_markers(frame)
    print("corners:", corners)
    if not ids == None:
        print("ids:", ids[0])
        ids_code = ids[0]
    print(ids_code)

    if ids_code != None and ids_code == 2:
        print(ids_code)
        yield session.call(
            "rie.dialogue.say", text="Red is certainly a beautiful colour!"
        )


@inlineCallbacks
def behavior(session):
    # Wrapper function to send the session to the callback function
    # otherwise only the frame is passed truough the subscriber
    def aruco_wrapper(frame):
        return aruco(session, frame)

    yield session.subscribe(aruco_wrapper, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")


@inlineCallbacks
def behavior_speech(session):
    global ids_code
    if ids_code is not None and ids_code == 2:
        print(ids_code)
        yield session.call(
            "rie.dialogue.say", text="Red is certainly a beautiful colour!"
        )


def main(session, details):
    global ids_code
    behavior(session)
    yield behavior_speech(session)


wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.66d1c84cafe50d23b76c5023",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
