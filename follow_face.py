import cv2
import base64
import numpy as np

def detect_face_in_frame(frame):
    """ Function to detect a face in a frame using OpenCV's Haar Cascade classifier
    
    Args:
        frame (dictionary):
        The frame dictionary from the robot's camera stream

    Returns:
        tuple: (top_left, bottom_right)
        The coordinates of the detected face in the frame
        
    """
    # Extract and preprocess the frame
    frame_single = frame["data"]["body.head.eyes"]
    # Ensure the frame is byte-like and decode from base64
    frame_single = bytes(frame_single, "utf-8")
    image_data = base64.b64decode(frame_single)

    # Convert the byte data to a NumPy array and decode it into an image
    np_array = np.frombuffer(image_data, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's pre-trained Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # If no face is detected, return None
    if len(faces) == 0:
        return None

    # Return the coordinates of the first detected face (x, y, width, height)
    x, y, w, h = faces[0]
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    
    return top_left, bottom_right
