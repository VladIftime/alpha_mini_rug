from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.util import sleep
from alpha_mini_rug import aruco_detect_markers
from alpha_mini_rug import key_words
from alpha_mini_rug import smart_questions
from alpha_mini_rug import follow_face
from alpha_mini_rug import perform_movement
from movements_test import perform_action_proportional_time
from camera_stream import show_camera_stream
from emotion import detect_face_and_emotion


@inlineCallbacks
def behavior_face(session):
    print("call")
    yield session.subscribe(detect_face, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    pass

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


@inlineCallbacks
def test_no_yield(session):
    yield session.call("rom.optional.behavior.play", name="BlocklyDab", sync=False)
    session.call(
        "rie.dialogue.say",
        text="Ja, ik been een appel en dat is lekker, Ja, ik been een appel en dat is lekker",
    )

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


# test no yield
@inlineCallbacks
def main_Test(session, details):
    yield test_no_yield(session)
    print("Reached the end")
    session.leave()


# test aruco markers
@inlineCallbacks
def main_Test2(session, details):
    # Try to see if we run infinite loop functions with yield what happens

    # should scan for aruco markers
    yield behavior(session)
    # should wave arms indefinitely
    # behviour2(session)

    print("Reached the end")


# test proprio
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
    frames = [
        {
            "time": 500,
            "data": {
                "body.head.yaw": 0,
            },
        },
    ]
    yield session.call("rom.actuator.motor.write", frames=frames, force=True, sync=True)
    yield follow_face(session)
    print("Reached the end")


# test movements
@inlineCallbacks
def main_Test5(session, details):
    # correct call
    # frames = [
    #     {
    #         "time": 100,
    #         "data": {
    #             "body.arms.left.lower.roll": -1.7,
    #             "body.arms.right.lower.roll": -1.70,
    #         },
    #     },
    #     {
    #         "time": 400,
    #         "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0},
    #     },
    # ]

    # angle out of bounds
    # frames = [{"time": 100, "data": {"body.arms.left.lower.roll": -9, "body.arms.right.lower.roll": -1.70}},
    # 		  {"time": 400, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]

    # invalid joint name
    frames = [{"time": 100, "data": {"body.arms.left.lower": -1, "body.arms.right.lower.roll": -1.70}},
    		  {"time": 400, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    sleep(10)
    yield session.call("rie.dialogue.say", text="This will be a fast move")
    yield session.call("rom.actuator.motor.write", frames=frames, force=True)

    sleep(10)

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    sleep(10)
    yield session.call("rie.dialogue.say", text="This will be a normal move")
    yield perform_action_proportional_time(session=session, frames=frames, force=True)

    session.leave()


# move all joints in position 0
@inlineCallbacks
def main_Test6(session, details):
    frames0 = [
        {
            "time": 1000,
            "data": {
                "body.head.yaw": 0,
                "body.head.roll": 0,
                "body.head.pitch": 0,
                "body.arms.right.upper.pitch": 0,
                "body.arms.right.lower.roll": 0,
                "body.arms.left.upper.pitch": 0,
                "body.arms.left.lower.roll": 0,
                "body.torso.yaw": 0,
                "body.legs.right.upper.pitch": 0,
                "body.legs.right.lower.pitch": 0,
                "body.legs.right.foot.roll": 0,
                "body.legs.left.upper.pitch": 0,
                "body.legs.left.lower.pitch": 0,
                "body.legs.left.foot.roll": 0,
            },
        }
    ]
    session.call("rom.actuator.motor.write", frames=frames0, force=True)

    session.leave()


# test keywords
@inlineCallbacks
def main_Test7(session, details):
    question_test = "What is your favorite color?"
    key_words_test = ["red", "blue", "green", "yellow", "pink", "orange", "purple"]
    key_words_answer = None

    yield session.call("rie.dialogue.config.language", lang="en")
    key_words_answer = yield key_words(
        session, question=question_test, key_words=key_words_test, time=1000, debug=True
    )

    print(key_words_answer)

    session.leave()


# test smart questions
@inlineCallbacks
def main_Test8(session, details):
    question_test = question_quiz = "What is the capital of Netherlands?"
    answers = {"amsterdam": ["amster", "dam", "amsterdam", "amsterd"]}

    answer = yield smart_questions(
        session=session, question=question_test, answer_dictionary=answers, debug=True
    )
    print(answer)
    session.leave()


# test camera stream
@inlineCallbacks
def main_Test9(session, details):
    yield session.subscribe(show_camera_stream, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    pass


@inlineCallbacks
def main_Test10(session, details):
    yield session.subscribe(detect_face_and_emotion, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")
    pass


@inlineCallbacks
def main_Test11(session, details):
    answer = yield smart_questions(
        session,
        "What is the capital of Netherlands?",
        {"amsterdam": ["amster", "dam", "amsterdam", "amsterd"]},
    )
    print("Answer:", answer)
    pass

@inlineCallbacks
def main_Test12(session, details):
    yield follow_face(session)
    pass

wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.66c6eff2afe50d23b76c0fa0",
)

wamp.on_join(main_Test11)

if __name__ == "__main__":
    run([wamp])
