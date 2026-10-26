# detector.py
import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        normalized_landmarks = None
        raw_landmarks = []

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )

            for lm in hand_landmarks.landmark:
                raw_landmarks.append([lm.x, lm.y, lm.z])

            raw_matrix = np.array(raw_landmarks)
            wrist_coords = raw_matrix[0, :]
            normalized_landmarks = raw_matrix - wrist_coords

        return frame, normalized_landmarks
