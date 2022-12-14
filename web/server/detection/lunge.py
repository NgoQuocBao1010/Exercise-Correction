import cv2, pickle
import mediapipe as mp
import numpy as np
import pandas as pd

from .utils import (
    calculate_angle,
    extract_important_keypoints,
    get_static_file_url,
    get_drawing_color,
)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def analyze_knee_angle(
    mp_results,
    stage: str,
    angle_thresholds: list,
    knee_over_toe: bool = False,
    draw_to_image: tuple = None,
) -> dict:
    """Calculate angle of each knee while performer at the DOWN position

    Args:
        mp_results (): MediaPipe Pose results
        stage (str): stage of the exercise
        angle_thresholds (list): lower and upper limits for the knee angles
        knee_over_toe (bool): if knee_over_toe error occur, ignore knee angles. Default to False
        draw_to_image (tuple, optional): Contains an OpenCV frame and its dimension. Defaults to None.

    Returns:
        dict: Statistic from analyze knee angles
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

    # Ignore checking for knee angle error if knee_over_toe error occur
    if knee_over_toe:
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

        if results["error"]:
            cv2.rectangle(image, (0, 50), (120, 100), (245, 117, 16), -1)
            cv2.putText(
                image,
                "KNEE ANGLE ERROR",
                (10, 62),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                "LEFT KNEE" if results["left"]["error"] else "RIGHT KNEE",
                (10, 82),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

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
    STAGE_ML_MODEL_PATH = get_static_file_url("model/lunge_stage_model.pkl")
    ERR_ML_MODEL_PATH = get_static_file_url("model/lunge_err_model.pkl")
    INPUT_SCALER_PATH = get_static_file_url("model/lunge_input_scaler.pkl")

    PREDICTION_PROB_THRESHOLD = 0.8
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
        if (
            not self.STAGE_ML_MODEL_PATH
            or not self.INPUT_SCALER_PATH
            or not self.ERR_ML_MODEL_PATH
        ):
            raise Exception("Cannot found lunge files for prediction")

        try:
            with open(self.ERR_ML_MODEL_PATH, "rb") as f:
                self.err_model = pickle.load(f)

            with open(self.STAGE_ML_MODEL_PATH, "rb") as f:
                self.stage_model = pickle.load(f)

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
            stage_predicted_class = self.stage_model.predict(X)[0]
            stage_prediction_probabilities = self.stage_model.predict_proba(X)[0]
            stage_prediction_probability = round(
                stage_prediction_probabilities[stage_prediction_probabilities.argmax()],
                2,
            )

            # Evaluate stage prediction for counter
            if (
                stage_predicted_class == "I"
                and stage_prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "init"
            elif (
                stage_predicted_class == "M"
                and stage_prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                self.current_stage = "mid"
            elif (
                stage_predicted_class == "D"
                and stage_prediction_probability >= self.PREDICTION_PROB_THRESHOLD
            ):
                if self.current_stage in ["init", "mid"]:
                    self.counter += 1

                self.current_stage = "down"

            # Check out errors from a rep to reduce repeated warning
            errors_from_this_rep = map(
                lambda el: el["stage"],
                filter(lambda el: el["counter"] == self.counter, self.results),
            )

            # Analyze lunge pose
            # Knee over toe
            k_o_t_error = None
            err_predicted_class = None
            err_prediction_probabilities = None
            err_prediction_probability = None
            if self.current_stage == "down":
                err_predicted_class = self.err_model.predict(X)[0]
                err_prediction_probabilities = self.err_model.predict_proba(X)[0]
                err_prediction_probability = round(
                    err_prediction_probabilities[err_prediction_probabilities.argmax()],
                    2,
                )

                if (
                    err_predicted_class == "L"
                    and err_prediction_probability >= self.PREDICTION_PROB_THRESHOLD
                ):
                    k_o_t_error = "Incorrect"
                    self.has_error = True

                    # Limit save error frames saved in a rep
                    if (
                        len(self.results) == 0
                        or "knee over toe" not in errors_from_this_rep
                    ):
                        self.results.append(
                            {
                                "stage": f"knee over toe",
                                "frame": image,
                                "timestamp": timestamp,
                                "counter": self.counter,
                            }
                        )

                elif (
                    err_predicted_class == "C"
                    and err_prediction_probability >= self.PREDICTION_PROB_THRESHOLD
                ):
                    k_o_t_error = "Correct"
                    self.has_error = False
            else:
                self.has_error = False

            # Analyze lunge pose
            # * Knee angle
            analyzed_results = analyze_knee_angle(
                mp_results=mp_results,
                stage=self.current_stage,
                angle_thresholds=self.KNEE_ANGLE_THRESHOLD,
                knee_over_toe=(k_o_t_error == "Incorrect"),
                draw_to_image=(image, video_dimensions),
            )

            # Stage management for saving results
            self.has_error = (
                analyzed_results["error"] if not self.has_error else self.has_error
            )
            if analyzed_results["error"]:
                # Limit save error frames saved in a rep
                if len(self.results) == 0 or "knee angle" not in errors_from_this_rep:
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
            cv2.rectangle(image, (0, 0), (325, 40), (245, 117, 16), -1)

            # Display Stage prediction for count
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
                f'{str(self.counter)}, {stage_predicted_class.split(" ")[0]}, {str(stage_prediction_probability)}',
                (5, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # Display KNEE_OVER_TOE error prediction
            cv2.putText(
                image,
                "KNEE_OVER_TOE",
                (145, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                f"{err_predicted_class}, {err_prediction_probability}, {k_o_t_error}",
                (135, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        except Exception as e:
            print(f"Error while detecting lunge errors: {e}")
