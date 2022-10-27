import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle

from .utils import calculate_distance, extract_important_keypoints, get_static_file_url

mp_pose = mp.solutions.pose


def analyze_feet_placement(results, visibility_threshold: int) -> int:
    """
    Calculate the ratio between the width of 2 knee to the shoulder width

    Return result explanation:
        -1: Unknown result due to poor visibility
        0: Correct knee placement
        1: knee placement too tight
        2: knee placement too wide
    """

    landmarks = results.pose_landmarks.landmark

    # Analyze visibility
    left_shoulder_vis = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility
    right_shoulder_vis = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility

    left_ankle_vis = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility
    right_ankle_vis = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility

    # If visibility of any keypoints is low cancel the analysis
    if (
        left_shoulder_vis < visibility_threshold
        or right_shoulder_vis < visibility_threshold
        or left_ankle_vis < visibility_threshold
        or right_ankle_vis < visibility_threshold
    ):
        return -1

    # Calculate shoulder width
    left_shoulder = [
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
    ]
    right_shoulder = [
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
    ]

    shoulder_width = calculate_distance(left_shoulder, right_shoulder)

    # Calculate 2-feet width
    left_ankle = [
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
    ]
    right_ankle = [
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
    ]

    feet_width = calculate_distance(left_ankle, right_ankle)

    # Calculate feet and shoulder ratio
    feet_shoulder_ratio = round(feet_width / shoulder_width, 1)

    if 1 <= feet_shoulder_ratio <= 1.7:
        return 0
    elif feet_shoulder_ratio < 1:
        return 1
    elif feet_shoulder_ratio > 1.7:
        return 2


def analyze_knee_placement(results, stage: str, visibility_threshold: int) -> int:
    """
    Calculate the ratio between the width of 2 knee to the foot width

    Return result explanation:
        -1: Unknown result due to poor visibility
        0: Correct knee placement
        1: Knee placement too tight
        2: Knee placement too wide
    """
    landmarks = results.pose_landmarks.landmark

    # Analyze visibility
    left_ankle_vis = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility
    right_ankle_vis = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility

    left_knee_vis = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
    right_knee_vis = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility

    # If visibility of any keypoints is low cancel the analysis
    if (
        left_ankle_vis < visibility_threshold
        or right_ankle_vis < visibility_threshold
        or left_knee_vis < visibility_threshold
        or right_knee_vis < visibility_threshold
    ):
        return -1

    # Calculate 2-feet width
    left_ankle = [
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
    ]
    right_ankle = [
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
    ]

    feet_width = calculate_distance(left_ankle, right_ankle)

    # Calculate 2 knee width
    left_knee = [
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y,
    ]
    right_knee = [
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
    ]

    knee_width = calculate_distance(left_knee, right_knee)

    # Calculate feet and shoulder ratio
    knee_feet_ratio = round(knee_width / feet_width, 1)

    # Body in UP position
    if stage == "up":
        if 0.6 <= knee_feet_ratio <= 1.2:
            return 0
        elif knee_feet_ratio < 0.6:
            return 1
        elif knee_feet_ratio > 1.2:
            return 2
    # Body in DOWN position
    else:
        if 0.8 <= knee_feet_ratio <= 1.3:
            return 0
        elif knee_feet_ratio < 0.8:
            return 1
        elif knee_feet_ratio > 1.3:
            return 2


class SquatDetection:
    ML_MODEL_PATH = get_static_file_url("model/squat_model.pkl")

    PREDICTION_PROB_THRESHOLD = 0.7
    VISIBILITY_THRESHOLD = 0.6

    def __init__(self) -> None:
        self.init_important_landmarks()

        self.current_stage = ""
        self.counter = 0

    def init_important_landmarks(self) -> None:
        """
        Determine Important landmarks for squat detection
        """

        self.important_landmarks = [
            "NOSE",
            "LEFT_SHOULDER",
            "RIGHT_SHOULDER",
            "LEFT_HIP",
            "RIGHT_HIP",
            "LEFT_KNEE",
            "RIGHT_KNEE",
            "LEFT_ANKLE",
            "RIGHT_ANKLE",
        ]

        # Generate all columns of the data frame
        self.headers = ["label"]  # Label column

        for lm in self.important_landmarks:
            self.headers += [
                f"{lm.lower()}_x",
                f"{lm.lower()}_y",
                f"{lm.lower()}_z",
                f"{lm.lower()}_v",
            ]

    def load_machine_learning_model(self) -> None:
        """
        Load machine learning model
        """
        if not self.ML_MODEL_PATH:
            raise Exception("Cannot found squat model")

        try:
            with open(self.ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
        except Exception as e:
            raise Exception(f"Error loading model, {e}")

    def detect(self, mp_results, image) -> None:
        """
        Make Squat Errors detection
        """
        try:
            # * Model prediction for SQUAT counter
            # Extract keypoints from frame for the input
            row = extract_important_keypoints(mp_results, self.important_landmarks)
            X = pd.DataFrame([row], columns=self.headers[1:])

            # Make prediction and its probability
            predicted_class = self.model.predict(X)[0]
            prediction_probabilities = self.model.predict_proba(X)[0]
            prediction_probability = round(
                prediction_probabilities[prediction_probabilities.argmax()], 2
            )

            # Evaluate model prediction
            if (
                predicted_class == "down"
                and prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "down"
            elif (
                self.current_stage == "down"
                and predicted_class == "up"
                and prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "up"
                self.counter += 1

            # * Evaluate FEET PLACEMENT error
            feet_placement_evaluation = analyze_feet_placement(
                mp_results, self.VISIBILITY_THRESHOLD
            )

            if feet_placement_evaluation == -1:
                feet_placement = "UNK"
            elif feet_placement_evaluation == 0:
                feet_placement = "Correct"
            elif feet_placement_evaluation == 1:
                feet_placement = "Too tight"
            elif feet_placement_evaluation == 2:
                feet_placement = "Too wide"

            # * Evaluate KNEE PLACEMENT error
            knee_placement_evaluation = analyze_knee_placement(
                mp_results, self.current_stage, self.VISIBILITY_THRESHOLD
            )

            if knee_placement_evaluation == -1:
                knee_placement = "UNK"
            elif knee_placement_evaluation == 0:
                knee_placement = "Correct"
            elif knee_placement_evaluation == 1:
                knee_placement = "Too tight"
            elif knee_placement_evaluation == 2:
                knee_placement = "Too wide"

            # Visualization
            # Status box
            cv2.rectangle(image, (0, 0), (500, 60), (245, 117, 16), -1)

            # Display class
            cv2.putText(
                image,
                "COUNT",
                (10, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                f'{str(self.counter)}, {predicted_class.split(" ")[0]}, {str(prediction_probability)}',
                (5, 40),
                cv2.FONT_HERSHEY_COMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Display Feet and Shoulder width ratio
            cv2.putText(
                image,
                "FEET",
                (200, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                feet_placement,
                (195, 40),
                cv2.FONT_HERSHEY_COMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Display knee and Shoulder width ratio
            cv2.putText(
                image,
                "KNEE",
                (330, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                knee_placement,
                (325, 40),
                cv2.FONT_HERSHEY_COMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        except Exception as e:
            print(f"Error while detecting squat errors: {e}")
