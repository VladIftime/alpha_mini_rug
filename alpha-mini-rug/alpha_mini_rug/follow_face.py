import cv2
import base64
import numpy as np
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def follow_face(session):
    """Function to subscribe to the robot's camera stream and follow a detected face

    Args:
        session (Component):
        The session object for the connection to the robot

    """

    # Wrapper to send the session to the callback function
    # otherwise we can only send the frame
    def center_face_wrapper(frame):
        return center_face(session, frame)

    yield session.subscribe(center_face_wrapper, "rom.sensor.sight.stream")
    yield session.call("rom.sensor.sight.stream")


def detect_face_in_frame(frame):
    """Function to detect a face in a frame using OpenCV's Haar Cascade classifier

    Args:
        frame (dictionary):
        The frame dictionary from the robot's camera stream

    Returns:
        tuple: (top_left, bottom_right)
        The coordinates of the detected face in the frame

    """
    frame_single = frame["data"]["body.head.eyes"]

    frame_single = bytes(frame_single, "utf-8")

    image_data = base64.b64decode(frame_single)

    np_array = np.frombuffer(image_data, dtype=np.uint8)

    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    if top_left is not None:
        return top_left, bottom_right


@inlineCallbacks
def center_face(session, frame):
    """
    Function to center the robot's head on a detected face by measuring the face's position in the frame, the robot's head position, and moving the head accordingly

    Args:
        session (Component):
        The session object for the connection to the robot

        frame (dictionary):
        The frame dictionary from the robot's camera stream

    Returns:
        None
    """
    center = None
    result = detect_face_in_frame(frame)
    if result is not None:
        top_left, bottom_right = result
        # Calculate the center of the detected face
        center = (
            (top_left[0] + bottom_right[0]) // 2,
            (top_left[1] + bottom_right[1]) // 2,
        )

    if center and center[0] > 155:
        motors = yield session.call("rom.sensor.proprio.read")
        head_motors = motors[0]["data"]["body.head.yaw"]
        frames = [
            {
                "time": 100,
                "data": {
                    "body.head.yaw": head_motors - 0.06,
                },
            },
        ]
        yield session.call(
            "rom.actuator.motor.write", frames=frames, force=True, sync=True
        )
    elif center and center[0] < 125:
        motors = yield session.call("rom.sensor.proprio.read")
        head_motors = motors[0]["data"]["body.head.yaw"]
        frames = [
            {
                "time": 100,
                "data": {
                    "body.head.yaw": head_motors + 0.06,
                },
            },
        ]
        yield session.call(
            "rom.actuator.motor.write", frames=frames, force=True, sync=True
        )
