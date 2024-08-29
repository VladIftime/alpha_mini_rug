import cv2
import numpy as np
import base64


def aruco_detect_markers(frame):
    """
    Args:
    frame (dictionary):
        The frame dictionary from the robot's camera stream
    Returns
        corners: list
        The corners of the detected markers
        ids: list
        The ids of the detected markers
    """
    if frame is None:
        raise ValueError("The frame is empty")
    if not isinstance(frame, dict):
        raise TypeError("The frame is not a dictionary")

    frame_single = frame["data"]["body.head.eyes"]

    frame_single = bytes(frame_single, "utf-8")

    image_data = base64.b64decode(frame_single)

    nparr = np.frombuffer(image_data, np.uint8)

    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Load the dictionary that was used to generate the markers
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, ids, rejectedImgPoints = detector.detectMarkers(image)

    return corners, ids
