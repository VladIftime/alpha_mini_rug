import cv2
import base64
import numpy as np


def detect_face_and_emotion(frame):
    # Extract and preprocess the frame
    frame_single = frame["data"]["body.head.eyes"]
    frame_single = bytes(frame_single, "utf-8")
    image_data = base64.b64decode(frame_single)

    np_array = np.frombuffer(image_data, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's pre-trained face and smile detector models
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    smile_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_smile.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        return None, None

    # Assume we're working with the first detected face
    x, y, w, h = faces[0]
    face_roi = gray[y : y + h, x : x + w]

    # Detect smile in the face ROI
    smiles = smile_cascade.detectMultiScale(
        face_roi, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25)
    )

    # Determine emotion based on whether a smile was detected
    if len(smiles) > 0:
        emotion = "Happy"
    else:
        emotion = "Neutral"

    # Return the face coordinates and detected emotion
    top_left = (x, y)
    bottom_right = (x + w, y + h)

    print(emotion)
