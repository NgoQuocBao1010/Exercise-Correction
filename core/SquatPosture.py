import cv2
import mediapipe as mp
import math
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

IMPORTANT_LANDMARKS = [
    "NOSE",
    "LEFT_EYE",
    "RIGHT_EYE",
    "MOUTH_LEFT",
    "MOUTH_RIGHT",
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "RIGHT_WRIST",
    "LEFT_WRIST",
    "LEFT_HIP",
    "RIGHT_HIP",
    "LEFT_KNEE",
    "RIGHT_KNEE",
    "LEFT_HEEL",
    "RIGHT_HEEL",
    "LEFT_FOOT_INDEX",
    "RIGHT_FOOT_INDEX",
    "LEFT_ANKLE",
    "RIGHT_ANKLE",
]


def get_params(pose_detections):
    if pose_detections.pose_landmarks is None:
        return np.array([0, 0])

    points = {}
    for lm in IMPORTANT_LANDMARKS:
        lm_coords = pose_detections.pose_landmarks.landmark[mp_pose.PoseLandmark[lm]]
        points[lm] = np.array([lm_coords.x, lm_coords.y, lm_coords.z])

    print(points)
