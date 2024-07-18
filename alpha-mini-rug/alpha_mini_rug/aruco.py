import cv2
import numpy as np
import base64


def aruco_detect_markers(frame):
    """
    frame: dict
        The frame dictionary from the robot's camera stream
    Returns
    -------
    corners: list
        The corners of the detected markers
    ids: list
        The ids of the detected markers
    """
    frame_single = frame["data"]["body.head.eyes"]
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

    return corners, ids
