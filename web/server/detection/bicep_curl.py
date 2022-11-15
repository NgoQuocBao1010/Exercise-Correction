from tabnanny import verbose
import mediapipe as mp
import cv2
import numpy as np
import pandas as pd
import pickle

from .utils import calculate_angle, extract_important_keypoints, get_static_file_url

mp_pose = mp.solutions.pose


class BicepPoseAnalysis:
    def __init__(
        self,
        side: str,
        stage_down_threshold: float,
        stage_up_threshold: float,
        peak_contraction_threshold: float,
        loose_upper_arm_angle_threshold: float,
        visibility_threshold: float,
    ):
        # Initialize thresholds
        self.stage_down_threshold = stage_down_threshold
        self.stage_up_threshold = stage_up_threshold
        self.peak_contraction_threshold = peak_contraction_threshold
        self.loose_upper_arm_angle_threshold = loose_upper_arm_angle_threshold
        self.visibility_threshold = visibility_threshold

        self.side = side
        self.counter = 0
        self.stage = "down"
        self.is_visible = True
        self.detected_errors = {
            "LOOSE_UPPER_ARM": 0,
            "PEAK_CONTRACTION": 0,
        }

        # Params for loose upper arm error detection
        self.loose_upper_arm = False

        # Params for peak contraction error detection
        self.peak_contraction_angle = 1000
        self.peak_contraction_frame = None

    def get_joints(self, landmarks) -> bool:
        """
        Check for joints' visibility then get joints coordinate
        """
        side = self.side.upper()

        # Check visibility
        joints_visibility = [
            landmarks[mp_pose.PoseLandmark[f"{side}_SHOULDER"].value].visibility,
            landmarks[mp_pose.PoseLandmark[f"{side}_ELBOW"].value].visibility,
            landmarks[mp_pose.PoseLandmark[f"{side}_WRIST"].value].visibility,
        ]

        is_visible = all([vis > self.visibility_threshold for vis in joints_visibility])
        self.is_visible = is_visible

        if not is_visible:
            return self.is_visible

        # Get joints' coordinates
        self.shoulder = [
            landmarks[mp_pose.PoseLandmark[f"{side}_SHOULDER"].value].x,
            landmarks[mp_pose.PoseLandmark[f"{side}_SHOULDER"].value].y,
        ]
        self.elbow = [
            landmarks[mp_pose.PoseLandmark[f"{side}_ELBOW"].value].x,
            landmarks[mp_pose.PoseLandmark[f"{side}_ELBOW"].value].y,
        ]
        self.wrist = [
            landmarks[mp_pose.PoseLandmark[f"{side}_WRIST"].value].x,
            landmarks[mp_pose.PoseLandmark[f"{side}_WRIST"].value].y,
        ]

        return self.is_visible

    def analyze_pose(self, landmarks, frame, results: list, timestamp: int):
        """
        - Bicep Counter
        - Errors Detection
        """
        self.get_joints(landmarks)

        # Cancel calculation if visibility is poor
        if not self.is_visible:
            return (None, None)

        # * Calculate curl angle for counter
        bicep_curl_angle = int(calculate_angle(self.shoulder, self.elbow, self.wrist))
        if bicep_curl_angle > self.stage_down_threshold:
            self.stage = "down"
        elif bicep_curl_angle < self.stage_up_threshold and self.stage == "down":
            self.stage = "up"
            self.counter += 1

        # * Calculate the angle between the upper arm (shoulder & joint) and the Y axis
        shoulder_projection = [
            self.shoulder[0],
            1,
        ]  # Represent the projection of the shoulder to the X axis
        ground_upper_arm_angle = int(
            calculate_angle(self.elbow, self.shoulder, shoulder_projection)
        )

        # * Evaluation for LOOSE UPPER ARM error
        if ground_upper_arm_angle > self.loose_upper_arm_angle_threshold:
            # Limit the saved frame
            if not self.loose_upper_arm:
                self.loose_upper_arm = True
                # save_frame_as_image(frame, f"Loose upper arm: {ground_upper_arm_angle}")
                self.detected_errors["LOOSE_UPPER_ARM"] += 1
                results.append(
                    {"stage": "loose upper arm", "frame": frame, "timestamp": timestamp}
                )
        else:
            self.loose_upper_arm = False

        # * Evaluate PEAK CONTRACTION error
        if self.stage == "up" and bicep_curl_angle < self.peak_contraction_angle:
            # Save peaked contraction every rep
            self.peak_contraction_angle = bicep_curl_angle
            self.peak_contraction_frame = frame

        elif self.stage == "down":
            # * Evaluate if the peak is higher than the threshold if True, marked as an error then saved that frame
            if (
                self.peak_contraction_angle != 1000
                and self.peak_contraction_angle >= self.peak_contraction_threshold
            ):
                # save_frame_as_image(self.peak_contraction_frame, f"{self.side} - Peak Contraction: {self.peak_contraction_angle}")
                self.detected_errors["PEAK_CONTRACTION"] += 1
                results.append(
                    {
                        "stage": "peak contraction",
                        "frame": self.peak_contraction_frame,
                        "timestamp": timestamp,
                    }
                )

            # Reset params
            self.peak_contraction_angle = 1000
            self.peak_contraction_frame = None

        return (bicep_curl_angle, ground_upper_arm_angle)

    def get_counter(self) -> int:
        return self.counter

    def reset(self):
        self.counter = 0
        self.stage = "down"
        self.is_visible = True
        self.detected_errors = {
            "LOOSE_UPPER_ARM": 0,
            "PEAK_CONTRACTION": 0,
        }

        # Params for loose upper arm error detection
        self.loose_upper_arm = False

        # Params for peak contraction error detection
        self.peak_contraction_angle = 1000
        self.peak_contraction_frame = None


class BicepCurlDetection:
    ML_MODEL_PATH = get_static_file_url("model/bicep_curl_model.pkl")
    INPUT_SCALER = get_static_file_url("model/bicep_curl_input_scaler.pkl")

    VISIBILITY_THRESHOLD = 0.65

    # Params for counter
    STAGE_UP_THRESHOLD = 90
    STAGE_DOWN_THRESHOLD = 120

    # Params to catch FULL RANGE OF MOTION error
    PEAK_CONTRACTION_THRESHOLD = 60

    # LOOSE UPPER ARM error detection
    LOOSE_UPPER_ARM = False
    LOOSE_UPPER_ARM_ANGLE_THRESHOLD = 40

    # STANDING POSTURE error detection
    POSTURE_ERROR_THRESHOLD = 0.95

    def __init__(self) -> None:
        self.init_important_landmarks()
        self.load_machine_learning_model()

        self.left_arm_analysis = BicepPoseAnalysis(
            side="left",
            stage_down_threshold=self.STAGE_DOWN_THRESHOLD,
            stage_up_threshold=self.STAGE_UP_THRESHOLD,
            peak_contraction_threshold=self.PEAK_CONTRACTION_THRESHOLD,
            loose_upper_arm_angle_threshold=self.LOOSE_UPPER_ARM_ANGLE_THRESHOLD,
            visibility_threshold=self.VISIBILITY_THRESHOLD,
        )

        self.right_arm_analysis = BicepPoseAnalysis(
            side="right",
            stage_down_threshold=self.STAGE_DOWN_THRESHOLD,
            stage_up_threshold=self.STAGE_UP_THRESHOLD,
            peak_contraction_threshold=self.PEAK_CONTRACTION_THRESHOLD,
            loose_upper_arm_angle_threshold=self.LOOSE_UPPER_ARM_ANGLE_THRESHOLD,
            visibility_threshold=self.VISIBILITY_THRESHOLD,
        )

        self.stand_posture = 0
        self.previous_stand_posture = 0
        self.results = []

    def init_important_landmarks(self) -> None:
        """
        Determine Important landmarks for plank detection
        """

        self.important_landmarks = [
            "NOSE",
            "LEFT_SHOULDER",
            "RIGHT_SHOULDER",
            "RIGHT_ELBOW",
            "LEFT_ELBOW",
            "RIGHT_WRIST",
            "LEFT_WRIST",
            "LEFT_HIP",
            "RIGHT_HIP",
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
            raise Exception("Cannot found plank model")

        try:
            with open(self.ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)

            with open(self.INPUT_SCALER, "rb") as f2:
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

        return self.results, {
            "left_counter": self.left_arm_analysis.get_counter(),
            "right_counter": self.right_arm_analysis.get_counter(),
        }

    def clear_results(self) -> None:
        self.stand_posture = 0
        self.previous_stand_posture = 0
        self.results = []

        self.right_arm_analysis.reset()
        self.left_arm_analysis.reset()

    def detect(self, mp_results, image, timestamp) -> None:
        """
        Make Bicep Curl errors detection
        """
        try:
            video_dimensions = [image.shape[1], image.shape[0]]
            landmarks = mp_results.pose_landmarks.landmark

            (
                left_bicep_curl_angle,
                left_ground_upper_arm_angle,
            ) = self.left_arm_analysis.analyze_pose(
                landmarks=landmarks,
                frame=image,
                results=self.results,
                timestamp=timestamp,
            )
            (
                right_bicep_curl_angle,
                right_ground_upper_arm_angle,
            ) = self.right_arm_analysis.analyze_pose(
                landmarks=landmarks,
                frame=image,
                results=self.results,
                timestamp=timestamp,
            )

            # Extract keypoints from frame for the input
            row = extract_important_keypoints(mp_results, self.important_landmarks)
            X = pd.DataFrame(
                [
                    row,
                ],
                columns=self.headers[1:],
            )
            X = pd.DataFrame(self.input_scaler.transform(X))

            # Make prediction and its probability
            prediction = self.model.predict(X, verbose=0)
            predicted_class = np.argmax(prediction, axis=1)[0]
            prediction_probability = max(prediction.tolist()[0])

            if prediction_probability >= self.POSTURE_ERROR_THRESHOLD:
                self.stand_posture = predicted_class

            # Visualization
            # Status box
            cv2.rectangle(image, (0, 0), (500, 40), (245, 117, 16), -1)

            # Display probability
            cv2.putText(
                image,
                "RIGHT",
                (15, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.right_arm_analysis.counter)
                if self.right_arm_analysis.is_visible
                else "UNK",
                (10, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Display Left Counter
            cv2.putText(
                image,
                "LEFT",
                (95, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.left_arm_analysis.counter)
                if self.left_arm_analysis.is_visible
                else "UNK",
                (100, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # * Display error
            # Right arm error
            cv2.putText(
                image,
                "R_PC",
                (165, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.right_arm_analysis.detected_errors["PEAK_CONTRACTION"]),
                (160, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                "R_LUA",
                (225, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.right_arm_analysis.detected_errors["LOOSE_UPPER_ARM"]),
                (220, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Left arm error
            cv2.putText(
                image,
                "L_PC",
                (300, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.left_arm_analysis.detected_errors["PEAK_CONTRACTION"]),
                (295, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                "L_LUA",
                (380, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str(self.left_arm_analysis.detected_errors["LOOSE_UPPER_ARM"]),
                (375, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Lean back error
            cv2.putText(
                image,
                "LB",
                (460, 12),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                image,
                str("C" if self.stand_posture == 0 else "L")
                + f" ,{predicted_class}, {prediction_probability}",
                (440, 30),
                cv2.FONT_HERSHEY_COMPLEX,
                0.3,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # * Visualize angles
            # Visualize LEFT arm calculated angles
            if self.left_arm_analysis.is_visible:
                cv2.putText(
                    image,
                    str(left_bicep_curl_angle),
                    tuple(
                        np.multiply(
                            self.left_arm_analysis.elbow, video_dimensions
                        ).astype(int)
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    image,
                    str(left_ground_upper_arm_angle),
                    tuple(
                        np.multiply(
                            self.left_arm_analysis.shoulder, video_dimensions
                        ).astype(int)
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            # Visualize RIGHT arm calculated angles
            if self.right_arm_analysis.is_visible:
                cv2.putText(
                    image,
                    str(right_bicep_curl_angle),
                    tuple(
                        np.multiply(
                            self.right_arm_analysis.elbow, video_dimensions
                        ).astype(int)
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 255, 0),
                    1,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    image,
                    str(right_ground_upper_arm_angle),
                    tuple(
                        np.multiply(
                            self.right_arm_analysis.shoulder, video_dimensions
                        ).astype(int)
                    ),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

            # Stage management for saving results
            if self.stand_posture == 1:
                if self.previous_stand_posture == self.stand_posture:
                    pass
                elif self.previous_stand_posture != self.stand_posture:
                    self.results.append(
                        {
                            "stage": "lean too far back",
                            "frame": image,
                            "timestamp": timestamp,
                        }
                    )

            self.previous_stand_posture = self.stand_posture

        except Exception as e:
            print(f"Error while detecting bicep curl errors: {e}")
