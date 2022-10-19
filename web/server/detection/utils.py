import mediapipe as mp
import cv2
import numpy as np
import datetime

# Drawing helpers
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


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
