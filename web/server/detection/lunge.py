import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle

from .utils import (
    calculate_angle,
    extract_important_keypoints,
    get_static_file_url,
    get_drawing_color,
)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def analyze_knee_angle(
    mp_results, stage: str, angle_thresholds: list, draw_to_image: tuple = None
):
    """
    Calculate angle of each knee while performer at the DOWN position

    Return result explanation:
        error: True if at least 1 error
        right
            error: True if an error is on the right knee
            angle: Right knee angle
        left
            error: True if an error is on the left knee
            angle: Left knee angle
    """
    results = {
        "error": None,
        "right": {"error": None, "angle": None},
        "left": {"error": None, "angle": None},
    }

    landmarks = mp_results.pose_landmarks.landmark

    # Calculate right knee angle
    right_hip = [
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y,
    ]
    right_knee = [
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
    ]
    right_ankle = [
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
    ]
    results["right"]["angle"] = calculate_angle(right_hip, right_knee, right_ankle)

    # Calculate left knee angle
    left_hip = [
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y,
    ]
    left_knee = [
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y,
    ]
    left_ankle = [
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
    ]
    results["left"]["angle"] = calculate_angle(left_hip, left_knee, left_ankle)

    # Draw to image
    if draw_to_image is not None and stage != "down":
        (image, video_dimensions) = draw_to_image

        # Visualize angles
        cv2.putText(
            image,
            str(int(results["right"]["angle"])),
            tuple(np.multiply(right_knee, video_dimensions).astype(int)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            str(int(results["left"]["angle"])),
            tuple(np.multiply(left_knee, video_dimensions).astype(int)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    if stage != "down":
        return results

    # Evaluation
    results["error"] = False

    if angle_thresholds[0] <= results["right"]["angle"] <= angle_thresholds[1]:
        results["right"]["error"] = False
    else:
        results["right"]["error"] = True
        results["error"] = True

    if angle_thresholds[0] <= results["left"]["angle"] <= angle_thresholds[1]:
        results["left"]["error"] = False
    else:
        results["left"]["error"] = True
        results["error"] = True

    # Draw to image
    if draw_to_image is not None:
        (image, video_dimensions) = draw_to_image

        right_color = (255, 255, 255) if not results["right"]["error"] else (0, 0, 255)
        left_color = (255, 255, 255) if not results["left"]["error"] else (0, 0, 255)

        # Visualize angles
        cv2.putText(
            image,
            str(int(results["right"]["angle"])),
            tuple(np.multiply(right_knee, video_dimensions).astype(int)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            right_color,
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            str(int(results["left"]["angle"])),
            tuple(np.multiply(left_knee, video_dimensions).astype(int)),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            left_color,
            1,
            cv2.LINE_AA,
        )

    return results


class LungeDetection:
    ML_MODEL_PATH = get_static_file_url("model/lunge_model.pkl")
    INPUT_SCALER_PATH = get_static_file_url("model/lunge_input_scaler.pkl")

    PREDICTION_PROB_THRESHOLD = 0.6
    KNEE_ANGLE_THRESHOLD = [60, 125]

    def __init__(self) -> None:
        self.init_important_landmarks()
        self.load_machine_learning_model()

        self.current_stage = ""
        self.counter = 0
        self.results = []
        self.has_error = False

    def init_important_landmarks(self) -> None:
        """
        Determine Important landmarks for lunge detection
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
            "LEFT_HEEL",
            "RIGHT_HEEL",
            "LEFT_FOOT_INDEX",
            "RIGHT_FOOT_INDEX",
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
        if not self.ML_MODEL_PATH or not self.INPUT_SCALER_PATH:
            raise Exception("Cannot found lunge model")

        try:
            with open(self.ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)

            with open(self.INPUT_SCALER_PATH, "rb") as f2:
                self.input_scaler = pickle.load(f2)
        except Exception as e:
            raise Exception(f"Error loading model, {e}")

    def handle_detected_results(self, video_name: str) -> tuple:
        """
        Save frame as evidence
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
        self.results = []
        self.counter = 0
        self.current_stage = ""
        self.has_error = False

    def detect(self, mp_results, image, timestamp) -> None:
        """
        Make Lunge Errors detection
        """
        try:
            video_dimensions = [image.shape[1], image.shape[0]]

            # * Model prediction for LUNGE counter
            # Extract keypoints from frame for the input
            row = extract_important_keypoints(mp_results, self.important_landmarks)
            X = pd.DataFrame([row], columns=self.headers[1:])
            X = pd.DataFrame(self.input_scaler.transform(X))

            # Make prediction and its probability
            predicted_class = self.model.predict(X)[0]
            prediction_probabilities = self.model.predict_proba(X)[0]
            prediction_probability = round(
                prediction_probabilities[prediction_probabilities.argmax()], 2
            )

            # Evaluate stage prediction for counter
            if (
                predicted_class == "I"
                and prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "init"
            elif (
                predicted_class == "M"
                and prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "mid"
            elif (
                predicted_class == "D"
                and prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                if self.current_stage == "mid":
                    self.counter += 1

                self.current_stage = "down"

            # Analyze lunge pose
            analyzed_results = analyze_knee_angle(
                mp_results=mp_results,
                stage=self.current_stage,
                angle_thresholds=self.KNEE_ANGLE_THRESHOLD,
                draw_to_image=(image, video_dimensions),
            )

            # Stage management for saving results
            self.has_error = analyzed_results["error"]
            if analyzed_results["error"]:
                # Limit the error frames saved in a rep
                if len(self.results) == 0:
                    self.results.append(
                        {
                            "stage": f"knee angle",
                            "frame": image,
                            "timestamp": timestamp,
                            "counter": self.counter,
                        }
                    )
                else:
                    last_error_counter = self.results[-1]["counter"]
                    if self.counter != last_error_counter:
                        self.results.append(
                            {
                                "stage": f"knee angle",
                                "frame": image,
                                "timestamp": timestamp,
                                "counter": self.counter,
                            }
                        )

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

        except Exception as e:
            print(f"Error while detecting lunge errors: {e}")
