import cv2
import mediapipe as mp
import numpy as np
import time
from pathlib import Path

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetector:
    HAND_CONNECTIONS = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),
        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),
        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),
        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),
        (0, 17),
    ]

    def __init__(self, max_hands=1, detection_confidence=0.5, tracking_confidence=0.6):
        model_path = Path(__file__).parent / "hand_landmarker.task"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Download hand_landmarker.task and place it "
                "beside detector.py."
            )

        base_options = python.BaseOptions(model_asset_path=str(model_path))

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self.landmarker = vision.HandLandmarker.create_from_options(options)

        self.timestamp_ms = 0

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # VIDEO mode requires increasing timestamps.
        self.timestamp_ms = max(self.timestamp_ms + 1, time.monotonic_ns() // 1_000_000)

        results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)

        normalized_landmarks = None

        if results.hand_landmarks:
            hand_landmarks = results.hand_landmarks[0]

            height, width = frame.shape[:2]
            raw_landmarks = []

            for lm in hand_landmarks:
                raw_landmarks.append([lm.x, lm.y, lm.z])

            raw_matrix = np.array(raw_landmarks, dtype=np.float32)

            # Make all coordinates relative to the wrist.
            wrist_coords = raw_matrix[0, :]
            normalized_landmarks = raw_matrix - wrist_coords

            # Draw landmarks and connections on the camera frame.
            points = []

            for lm in hand_landmarks:
                x = int(lm.x * width)
                y = int(lm.y * height)
                points.append((x, y))

            for start, end in self.HAND_CONNECTIONS:
                cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

            for x, y in points:
                cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)

        return frame, normalized_landmarks

    def close(self):
        self.landmarker.close()
