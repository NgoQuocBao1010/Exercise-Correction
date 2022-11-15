import mediapipe as mp
import cv2
import numpy as np
import datetime
import os
import math
from django.conf import settings

# Drawing helpers
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# * Mediapipe Utils Functions
def calculate_angle(point1: list, point2: list, point3: list) -> float:
    """
    Calculate the angle between 3 points
    Unit of the angle will be in Degree
    """
    point1 = np.array(point1)
    point2 = np.array(point2)
    point3 = np.array(point3)

    # Calculate algo
    angleInRad = np.arctan2(point3[1] - point2[1], point3[0] - point2[0]) - np.arctan2(
        point1[1] - point2[1], point1[0] - point2[0]
    )
    angleInDeg = np.abs(angleInRad * 180.0 / np.pi)

    angleInDeg = angleInDeg if angleInDeg <= 180 else 360 - angleInDeg
    return angleInDeg


def calculate_distance(pointX, pointY) -> float:
    """
    Calculate a distance between 2 points
    """

    x1, y1 = pointX
    x2, y2 = pointY

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def extract_important_keypoints(results, important_landmarks: list) -> list:
    """
    Extract important keypoints from mediapipe pose detection
    """
    landmarks = results.pose_landmarks.landmark

    data = []
    for lm in important_landmarks:
        keypoint = landmarks[mp_pose.PoseLandmark[lm].value]
        data.append([keypoint.x, keypoint.y, keypoint.z, keypoint.visibility])

    return np.array(data).flatten().tolist()


# * OpenCV util functions
def rescale_frame(frame, percent=50):
    """
    Rescale a frame from OpenCV to a certain percentage compare to its original frame
    """
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def save_frame_as_image(frame, message: str = None):
    """
    Save a frame as image to display the error
    """
    now = datetime.datetime.now()

    if message:
        cv2.putText(
            frame,
            message,
            (50, 150),
            cv2.FONT_HERSHEY_COMPLEX,
            0.4,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    print("Saving ...")
    cv2.imwrite(f"../data/logs/bicep_{now}.jpg", frame)


# * Other util functions
def get_static_file_url(file_name: str) -> str:
    """
    Return static url of a file
    Return None if file is not exist
    """

    path = f"{settings.STATICFILES_DIRS[0]}/{file_name}"

    return path if os.path.exists(path) else None


def get_drawing_color(error: bool) -> dict:
    LIGHT_BLUE = (244, 117, 66)
    LIGHT_PINK = (245, 66, 230)

    LIGHT_RED = (29, 62, 199)
    LIGHT_YELLOW = (1, 143, 241)

    return (LIGHT_YELLOW, LIGHT_RED) if error else (LIGHT_BLUE, LIGHT_PINK)
