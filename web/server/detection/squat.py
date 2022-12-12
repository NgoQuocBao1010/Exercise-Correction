import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle

from .utils import (
    calculate_distance,
    extract_important_keypoints,
    get_static_file_url,
    get_drawing_color,
)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def analyze_foot_knee_placement(
    results,
    stage: str,
    foot_shoulder_ratio_thresholds: list,
    knee_foot_ratio_thresholds: dict,
    visibility_threshold: int,
) -> dict:
    """
    Calculate the ratio between the foot and shoulder for FOOT PLACEMENT analysis

    Calculate the ratio between the knee and foot for KNEE PLACEMENT analysis

    Return result explanation:
        -1: Unknown result due to poor visibility
        0: Correct knee placement
        1: Placement too tight
        2: Placement too wide
    """
    analyzed_results = {
        "foot_placement": -1,
        "knee_placement": -1,
    }

    landmarks = results.pose_landmarks.landmark

    # * Visibility check of important landmarks for foot placement analysis
    left_foot_index_vis = landmarks[
        mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
    ].visibility
    right_foot_index_vis = landmarks[
        mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value
    ].visibility

    left_knee_vis = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
    right_knee_vis = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility

    # If visibility of any keypoints is low cancel the analysis
    if (
        left_foot_index_vis < visibility_threshold
        or right_foot_index_vis < visibility_threshold
        or left_knee_vis < visibility_threshold
        or right_knee_vis < visibility_threshold
    ):
        return analyzed_results

    # * Calculate shoulder width
    left_shoulder = [
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
    ]
    right_shoulder = [
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
    ]
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)

    # * Calculate 2-foot width
    left_foot_index = [
        landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y,
    ]
    right_foot_index = [
        landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y,
    ]
    foot_width = calculate_distance(left_foot_index, right_foot_index)

    # * Calculate foot and shoulder ratio
    foot_shoulder_ratio = round(foot_width / shoulder_width, 1)

    # * Analyze FOOT PLACEMENT
    min_ratio_foot_shoulder, max_ratio_foot_shoulder = foot_shoulder_ratio_thresholds
    if min_ratio_foot_shoulder <= foot_shoulder_ratio <= max_ratio_foot_shoulder:
        analyzed_results["foot_placement"] = 0
    elif foot_shoulder_ratio < min_ratio_foot_shoulder:
        analyzed_results["foot_placement"] = 1
    elif foot_shoulder_ratio > max_ratio_foot_shoulder:
        analyzed_results["foot_placement"] = 2

    # * Visibility check of important landmarks for knee placement analysis
    left_knee_vis = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
    right_knee_vis = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility

    # If visibility of any keypoints is low cancel the analysis
    if left_knee_vis < visibility_threshold or right_knee_vis < visibility_threshold:
        print("Cannot see foot")
        return analyzed_results

    # * Calculate 2 knee width
    left_knee = [
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y,
    ]
    right_knee = [
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
    ]
    knee_width = calculate_distance(left_knee, right_knee)

    # * Calculate foot and shoulder ratio
    knee_foot_ratio = round(knee_width / foot_width, 1)

    # * Analyze KNEE placement
    up_min_ratio_knee_foot, up_max_ratio_knee_foot = knee_foot_ratio_thresholds.get(
        "up"
    )
    (
        middle_min_ratio_knee_foot,
        middle_max_ratio_knee_foot,
    ) = knee_foot_ratio_thresholds.get("middle")
    down_min_ratio_knee_foot, down_max_ratio_knee_foot = knee_foot_ratio_thresholds.get(
        "down"
    )

    if stage == "up":
        if up_min_ratio_knee_foot <= knee_foot_ratio <= up_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 0
        elif knee_foot_ratio < up_min_ratio_knee_foot:
            analyzed_results["knee_placement"] = 1
        elif knee_foot_ratio > up_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 2
    elif stage == "middle":
        if middle_min_ratio_knee_foot <= knee_foot_ratio <= middle_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 0
        elif knee_foot_ratio < middle_min_ratio_knee_foot:
            analyzed_results["knee_placement"] = 1
        elif knee_foot_ratio > middle_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 2
    elif stage == "down":
        if down_min_ratio_knee_foot <= knee_foot_ratio <= down_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 0
        elif knee_foot_ratio < down_min_ratio_knee_foot:
            analyzed_results["knee_placement"] = 1
        elif knee_foot_ratio > down_max_ratio_knee_foot:
            analyzed_results["knee_placement"] = 2

    return analyzed_results


class SquatDetection:
    ML_MODEL_PATH = get_static_file_url("model/squat_model.pkl")

    PREDICTION_PROB_THRESHOLD = 0.7
    VISIBILITY_THRESHOLD = 0.6
    FOOT_SHOULDER_RATIO_THRESHOLDS = [1.2, 2.8]
    KNEE_FOOT_RATIO_THRESHOLDS = {
        "up": [0.5, 1.0],
        "middle": [0.7, 1.0],
        "down": [0.7, 1.1],
    }

    def __init__(self) -> None:
        self.init_important_landmarks()
        self.load_machine_learning_model()

        self.current_stage = ""
        self.previous_stage = {
            "feet": "",
            "knee": "",
        }
        self.counter = 0
        self.results = []
        self.has_error = False

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

    def handle_detected_results(self, video_name: str) -> tuple:
        """
        Save error frame as evidence
        """
        file_name, _ = video_name.split(".")
        save_folder = get_static_file_url("images")
        for index, error in enumerate(self.results):
            try:
                image_name = f"{file_name}_{index}.jpg"
                cv2.imwrite(f"{save_folder}/{file_name}_{index}.jpg", error["frame"])
                self.results[index]["frame"] = image_name
            except Exception as e:
                print("ERROR cannot save frame: " + str(e))
                self.results[index]["frame"] = None

        return self.results, self.counter

    def clear_results(self) -> None:
        self.current_stage = ""
        self.previous_stage = {
            "feet": "",
            "knee": "",
        }
        self.counter = 0
        self.results = []
        self.has_error = False

    def detect(self, mp_results, image, timestamp) -> None:
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

            # Analyze squat pose
            analyzed_results = analyze_foot_knee_placement(
                results=mp_results,
                stage=self.current_stage,
                foot_shoulder_ratio_thresholds=self.FOOT_SHOULDER_RATIO_THRESHOLDS,
                knee_foot_ratio_thresholds=self.KNEE_FOOT_RATIO_THRESHOLDS,
                visibility_threshold=self.VISIBILITY_THRESHOLD,
            )

            foot_placement_evaluation = analyzed_results["foot_placement"]
            knee_placement_evaluation = analyzed_results["knee_placement"]

            # * Evaluate FEET PLACEMENT error
            if foot_placement_evaluation == -1:
                feet_placement = "unknown"
            elif foot_placement_evaluation == 0:
                feet_placement = "correct"
            elif foot_placement_evaluation == 1:
                feet_placement = "too tight"
            elif foot_placement_evaluation == 2:
                feet_placement = "too wide"

            # * Evaluate KNEE PLACEMENT error
            if knee_placement_evaluation == -1:
                knee_placement = "unknown"
            elif knee_placement_evaluation == 0:
                knee_placement = "correct"
            elif knee_placement_evaluation == 1:
                knee_placement = "too tight"
            elif knee_placement_evaluation == 2:
                knee_placement = "too wide"

            # Stage management for saving results
            # * Feet placement
            if feet_placement in ["too tight", "too wide"]:
                # Stage not change
                if self.previous_stage["feet"] == feet_placement:
                    pass
                # Stage from correct to error
                elif self.previous_stage["feet"] != feet_placement:
                    self.results.append(
                        {
                            "stage": f"feet {feet_placement}",
                            "frame": image,
                            "timestamp": timestamp,
                        }
                    )

                self.previous_stage["feet"] = feet_placement

            # * Knee placement
            if knee_placement in ["too tight", "too wide"]:
                # Stage not change
                if self.previous_stage["knee"] == knee_placement:
                    pass
                # Stage from correct to error
                elif self.previous_stage["knee"] != knee_placement:
                    self.results.append(
                        {
                            "stage": f"knee {knee_placement}",
                            "frame": image,
                            "timestamp": timestamp,
                        }
                    )

                self.previous_stage["knee"] = knee_placement

            if feet_placement in ["too tight", "too wide"] or knee_placement in [
                "too tight",
                "too wide",
            ]:
                self.has_error = True
            else:
                self.has_error = False

            # Visualization
            # Draw landmarks and connections
            landmark_color, connection_color = get_drawing_color(self.has_error)
            mp_drawing.draw_landmarks(
                image,
                mp_results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=landmark_color, thickness=2, circle_radius=2
                ),
                mp_drawing.DrawingSpec(
                    color=connection_color, thickness=2, circle_radius=1
                ),
            )

            # Status box
            cv2.rectangle(image, (0, 0), (300, 40), (245, 117, 16), -1)

            # Display class
            cv2.putText(
                image,
                "COUNT",
                (10, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                f'{str(self.counter)}, {predicted_class.split(" ")[0]}, {str(prediction_probability)}',
                (5, 25),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # Display Feet and Shoulder width ratio
            cv2.putText(
                image,
                "FEET",
                (130, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                feet_placement,
                (125, 25),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # Display knee and Shoulder width ratio
            cv2.putText(
                image,
                "KNEE",
                (225, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                knee_placement,
                (220, 25),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        except Exception as e:
            print(f"Error while detecting squat errors: {e}")
