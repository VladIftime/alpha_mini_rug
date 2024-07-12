from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.util import sleep
import cv2  # the OpenCV library (computer vision)
import numpy as np
import base64


def overlay_image(image, ids, corners):
    if ids is not None:
        # Draw detected markers
        image = cv2.aruco.drawDetectedMarkers(image, corners, ids)
        print("ids=", ids)
        print("corners=", corners)
        # Overlay an image onto each detected marker
        for i in range(len(ids)):
            marker_corners = corners[i][0]

            # Define the overlay image (for simplicity, using a colored square here)
            overlay = np.zeros((100, 100, 3), dtype=np.uint8)
            overlay[:] = (0, 255, 0)  # Green square

            # Define the destination points for the overlay
            dst_pts = np.array(marker_corners, dtype="float32")

            # Define the source points for the overlay
            src_pts = np.array([[0, 0], [99, 0], [99, 99], [0, 99]], dtype="float32")

            # Compute the perspective transform matrix
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)

            # Warp the overlay image to fit the marker
            warped_overlay = cv2.warpPerspective(
                overlay, M, (image.shape[1], image.shape[0])
            )

            # Create a mask for the overlay
            mask = cv2.warpPerspective(
                np.ones_like(overlay, dtype=np.uint8) * 255,
                M,
                (image.shape[1], image.shape[0]),
            )

            # Overlay the warped image onto the original image
            image = cv2.addWeighted(image, 1, warped_overlay, 0.5, 0)

    # Display the image
    cv2.imshow("ArUco Markers", image)
    cv2.waitKey(1)


class DetectionState:
    def __init__(self):
        self.deferred = None

    def get_deferred(self):
        if self.deferred is None or self.deferred.called:
            self.deferred = Deferred()
        return self.deferred


def detect_aruco_cards(frame, state):
    # This function is called each time the robot sees a change in the camera

    frame_single = frame["data"][
        "body.head.eyes"
    ]  # collecting the data from the stream
    # make sure the frame is byte-like and not a string; it's in base64
    frame_single = bytes(frame_single, "utf-8")
    # Decode the base64 string
    image_data = base64.b64decode(frame_single)

    # Convert the decoded bytes to a numpy array
    nparr = np.frombuffer(image_data, np.uint8)

    # Decode the numpy array into an image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Load the dictionary that was used to generate the markers
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = detector.detectMarkers(image)
    
    overlay_image(image, ids, corners)


@inlineCallbacks
def main(session, details):
    frames = yield session.call("rom.sensor.sight.read")
    frame_single = frames[0]["data"]
    print("")

    # Create a shared state object
    state = DetectionState()

    # Subscribe the camera (sight) stream to the system in the function vision(stream)
    yield session.subscribe(
        lambda frame: detect_aruco_cards(frame, state), "rom.sensor.sight.stream"
    )
    yield session.call(
        "rom.sensor.sight.sensitivity"
    )  # Set the sensitivity of the camera
    # and call the stream
    yield session.call("rom.sensor.sight.stream")
    print("Subscribed to the camera stream")

    while True:
        # Wait for the detection result
        ids, corners = yield state.get_deferred()
        print("Detected ArUco markers in main:")
        print("ids:", ids)
        print("corners:", corners)


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
