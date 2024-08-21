from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.util import sleep
from alpha_mini_rug import aruco_detect_markers
from follow_face import detect_face_in_frame
import threading


def detect_aruco_cards(frame):
    corners, ids = aruco_detect_markers(frame)
    if ids is not None:
        print("ids=", ids)


def detect_face(frame):
    top_left, bottom_right = detect_face_in_frame(frame)
    if top_left is not None:
        print("Face detected")
        print("Top left: ", top_left)
        print("Bottom right: ", bottom_right)
    pass


@inlineCallbacks
def behavior_face(session):
    yield session.subscribe(detect_face_in_frame, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    pass


@inlineCallbacks
def behavior(session):
    yield session.subscribe(detect_aruco_cards, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    pass


@inlineCallbacks
def behviour2(session):
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    # Command the robot to perform the waving movement with the right arm
    while True:
        yield session.call(
            "rom.actuator.motor.write",
            frames=[
                # Right arm wave motion
                #! NOTE: The elements of the 'data' dictionary have to always be the same for all the frames even if the value is the same(eg. we have to always have "body.arms.right.upper.pitch" and "body.arms.right.lower.roll" in the dictionary even if the value is the same for all the frames)
                {
                    "time": 0,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": 3,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": 3,
                    },
                },
                {
                    "time": 2000,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": 2,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": 2,
                    },
                },
                {
                    "time": 2200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": -1,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": -1,
                    },
                },
                {
                    "time": 3200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": 2,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": 2,
                    },
                },
                {
                    "time": 4200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": -1,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": -1,
                    },
                },
                {
                    "time": 5200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": 2,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": 2,
                    },
                },
                {
                    "time": 6200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": -1,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": -1,
                    },
                },
                {
                    "time": 7200,
                    "data": {
                        "body.arms.right.upper.pitch": -2.5,
                        "body.arms.right.lower.roll": 2,
                        "body.arms.left.upper.pitch": -2.5,
                        "body.arms.left.lower.roll": 2,
                    },
                },
            ],
            force=True,
            sync=True,
        )

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    pass


def test_no_yield(session):
    session.call("rie.dialogue.say", text="Ja")
    session.call("rom.optional.behavior.play", name="BlocklyRobotDance")
    pass


# ----------------------------------------------------------


def main_parallel_test(session, details):
    thread1 = threading.Thread(target=behavior(session))
    thread1.start()
    thread2 = threading.Thread(target=behviour2(session))
    thread2.start()
    thread1.join()
    thread2.join()
    print("Subscribed to the camera stream")


@inlineCallbacks
def main_Test(session, details):
    yield test_no_yield(session)
    print("Reached the end")


@inlineCallbacks
def main_Test2(session, details):
    # Try to see if we run infinite loop functions with yield what happens

    # should scan for aruco markers
    yield behavior(session)
    # should wave arms indefinitely
    yield behviour2(session)

    print("Reached the end")


@inlineCallbacks
def main_Test3(session, details):
    # Test if we can read the joints
    frame = yield session.call("rom.actuator.proprio.read")
    print("Motors data:")
    print(frame[0]["data"])
    print("Reached the end")


@inlineCallbacks
def main_Test4(session, details):
    # Test the face detection
    yield behavior_face(session)
    print("Reached the end")


wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.6698e1a90f3d8a1b0bad848f",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
