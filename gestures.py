import numpy as np


class GestureClassifier:
    def __init__(self):
        # MediaPipe landmark indices for the tips of the 5 fingers
        self.TIP_IDS = [4, 8, 12, 16, 20]

    def classify(self, landmarks):
        """
        Analyzes the spatial normalized landmarks array to classify the hand gesture.
        Returns a string naming the gesture and a dict of raw states for debugging.
        """
        if landmarks is None:
            return "No Hand Detected", {}

        fingers_open = []

        # 1. THUMB LOGIC: Check horizontal or vertical displacement relative to its base
        # Since landmarks are normalized to the wrist (0), we compare the thumb tip (4)
        # to the thumb base joint (2) horizontally.
        if landmarks[4][0] > landmarks[2][0]:
            fingers_open.append(1)  # Open / Extended
        else:
            fingers_open.append(0)  # Closed / Curled

        # 2. OTHER 4 FINGERS LOGIC: Compare finger tip Y-coordinate to the PIP joint (2 joints down)
        # Note: In computer vision screens, a lower Y value means higher up on the screen.
        for i in range(1, 5):
            tip_idx = self.TIP_IDS[i]
            pip_idx = tip_idx - 2

            if landmarks[tip_idx][1] < landmarks[pip_idx][1]:
                fingers_open.append(1)  # Finger is pointing up (Extended)
            else:
                fingers_open.append(0)  # Finger is curled down (Closed)

        # 3. GESTURE MAPPING: Translate open/closed finger configurations into explicit intents
        gesture_name = "Unknown"

        # Open Palm: All 5 fingers extended -> [1, 1, 1, 1, 1]
        if fingers_open == [1, 1, 1, 1, 1]:
            gesture_name = "Open Palm"

        # Peace Sign: Index and Middle extended, others curled -> [0, 1, 1, 0, 0]
        elif fingers_open == [0, 1, 1, 0, 0] or fingers_open == [
            1,
            1,
            1,
            0,
            0,
        ]:
            gesture_name = "Peace Sign"

        # Thumbs Up: Only thumb extended up, others curled, and thumb tip is higher than knuckle
        elif fingers_open == [1, 0, 0, 0, 0] and landmarks[4][1] < landmarks[3][1]:
            gesture_name = "Thumbs Up"

        # Fist: All fingers closed tightly -> [0, 0, 0, 0, 0]
        elif fingers_open == [0, 0, 0, 0, 0]:
            gesture_name = "Fist"

        return gesture_name, {"finger_states": fingers_open}
