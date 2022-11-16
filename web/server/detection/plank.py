import cv2
import numpy as np
import pandas as pd
import pickle
import mediapipe as mp

from .utils import extract_important_keypoints, get_static_file_url, get_drawing_color

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class PlankDetection:
    ML_MODEL_PATH = get_static_file_url("model/plank_model.pkl")
    INPUT_SCALER_PATH = get_static_file_url("model/plank_input_scaler.pkl")
    PREDICTION_PROBABILITY_THRESHOLD = 0.6

    def __init__(self) -> None:
        self.init_important_landmarks()
        self.load_machine_learning_model()

        self.previous_stage = "unknown"
        self.results = []
        self.has_error = False

    def init_important_landmarks(self) -> None:
        """
        Determine Important landmarks for plank detection
        """

        self.important_landmarks = [
            "NOSE",
            "LEFT_SHOULDER",
            "RIGHT_SHOULDER",
            "LEFT_ELBOW",
            "RIGHT_ELBOW",
            "LEFT_WRIST",
            "RIGHT_WRIST",
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
            raise Exception("Cannot found plank model file or input scaler file")

        try:
            with open(self.ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(self.INPUT_SCALER_PATH, "rb") as f2:
                self.input_scaler = pickle.load(f2)
        except Exception as e:
            raise Exception(f"Error loading model, {e}")

    def handle_detected_results(self, video_name: str) -> None:
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

        return self.results, self.previous_stage

    def clear_results(self) -> None:
        self.previous_stage = "unknown"
        self.results = []
        self.has_error = False

    def detect(self, mp_results, image, timestamp) -> None:
        """
        Make Plank Errors detection
        """
        try:
            # Extract keypoints from frame for the input
            row = extract_important_keypoints(mp_results, self.important_landmarks)
            X = pd.DataFrame([row], columns=self.headers[1:])
            X = pd.DataFrame(self.input_scaler.transform(X))

            # Make prediction and its probability
            predicted_class = self.model.predict(X)[0]
            prediction_probability = self.model.predict_proba(X)[0]

            # Evaluate model prediction
            if (
                predicted_class == "C"
                and prediction_probability[prediction_probability.argmax()]
                >= self.PREDICTION_PROBABILITY_THRESHOLD
            ):
                current_stage = "correct"
            elif (
                predicted_class == "L"
                and prediction_probability[prediction_probability.argmax()]
                >= self.PREDICTION_PROBABILITY_THRESHOLD
            ):
                current_stage = "low back"
            elif (
                predicted_class == "H"
                and prediction_probability[prediction_probability.argmax()]
                >= self.PREDICTION_PROBABILITY_THRESHOLD
            ):
                current_stage = "high back"
            else:
                current_stage = "unknown"

            # Stage management for saving results
            if current_stage in ["low back", "high back"]:
                # Stage not change
                if self.previous_stage == current_stage:
                    pass
                # Stage from correct to error
                elif self.previous_stage != current_stage:
                    self.results.append(
                        {"stage": current_stage, "frame": image, "timestamp": timestamp}
                    )
                    self.has_error = True
            else:
                self.has_error = False

            self.previous_stage = current_stage

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
            cv2.rectangle(image, (0, 0), (250, 60), (245, 117, 16), -1)

            # Display probability
            cv2.putText(
                image,
                "PROB",
                (15, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(
                    round(prediction_probability[np.argmax(prediction_probability)], 2)
                ),
                (10, 40),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Display class
            cv2.putText(
                image,
                "CLASS",
                (95, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                current_stage,
                (90, 40),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        except Exception as e:
            raise Exception(f"Error while detecting plank errors: {e}")
