import base64
import cv2
import numpy as np


def show_camera_stream(frame):
    """
    Display the robot's camera stream

    Args:
        frame (dictionary):
            The frame dictionary from the robot's camera stream
    Returns:
        None
    """
    # check if the frame is not empty
    if frame is None:
        raise ValueError("The frame is empty")
    # check if the frame is a dictionary
    if not isinstance(frame, dict):
        raise TypeError("The frame is not a dictionary")

    frame_single = frame["data"]["body.head.eyes"]
    # make sure the frame is byte-like and not a string; it's in base64
    frame_single = bytes(frame_single, "utf-8")
    # Decode the base64 string
    image_data = base64.b64decode(frame_single)

    # Convert the decoded bytes to a numpy array
    nparr = np.frombuffer(image_data, np.uint8)

    # Decode the numpy array into an image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Display the image and close it in 1 second
    cv2.imshow("Camera Stream", image)
    cv2.waitKey(100)
    
    pass
