import mediapipe as mp
import cv2
from django.conf import settings

from .utils import rescale_frame

# Drawing helpers
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def bicep_detection(path: str, file_name: str, rescale_percent: float = 40):
    cap = cv2.VideoCapture(path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * rescale_percent / 100 + 1)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * rescale_percent / 100 + 1)
    size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(f"{settings.MEDIA_ROOT}/{file_name}", fourcc, 15, size)

    print(f"PROCESSING VIDEO: {path}")

    with mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():
            ret, image = cap.read()

            if not ret:
                break

            image = rescale_frame(image, rescale_percent)

            # Recolor image from BGR to RGB for mediapipe
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            if not results.pose_landmarks:
                continue

            # Recolor image from BGR to RGB for mediapipe
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw landmarks and connections
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=(244, 117, 66), thickness=2, circle_radius=4
                ),
                mp_drawing.DrawingSpec(
                    color=(245, 66, 230), thickness=2, circle_radius=2
                ),
            )

            out.write(image)
