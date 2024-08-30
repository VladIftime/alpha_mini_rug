from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import aruco_detect_markers

check = 0 # when the aruco card #2 was seen, the check flag becomes 1

@inlineCallbacks
def aruco(session, frame):
    global ids_code
    global check
    corners, ids = aruco_detect_markers(frame)
    print("corners:", corners)
    print("ids:", ids)
    
    if not ids == None and ids[0] == 2 and check == 0:
        check = 1
        yield session.call("rie.dialogue.say", text="Red is certainly a beautiful color!")


@inlineCallbacks
def behavior(session):
    
    def aruco_wrapper(frame):
        return aruco(session, frame)
    
    yield session.subscribe(aruco_wrapper, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    

def main(session, details):
    behavior(session)
        

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
