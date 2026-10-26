import numpy as np


class GestureClassifier:
    def __init__(self, debounce_frames=6):
        # MediaPipe landmark indices for the structural tips of the 5 fingers
        self.TIP_IDS = [4, 8, 12, 16, 20]
        self.debounce_frames = debounce_frames
        self.current_stable_gesture = "No Hand Detected"
        self.candidate_gesture = "No Hand Detected"
        self.candidate_counter = 0

    def classify(self, landmarks):
        """
        Analyzes normalized spatial coordinate locations to classify raw hand orientations.
        Explicitly isolates X (0) and Y (1) matrix dimensions to protect vector operations.
        """
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", []

        fingers_open = []

        thumb_tip = landmarks
        index_base = landmarks
        thumb_to_index_dist = np.linalg.norm(thumb_tip - index_base)
        palm_size = np.linalg.norm(landmarks - landmarks)

        if thumb_to_index_dist > palm_size * 0.45:
            fingers_open.append(1)
        else:
            fingers_open.append(0)

        for i in range(1, 5):
            tip_idx = self.TIP_IDS[i]
            pip_idx = tip_idx - 2

            # Extracting only the Y coordinate [1] to isolate height thresholds
            if landmarks[tip_idx][1] < landmarks[pip_idx][1]:
                fingers_open.append(1)  # Extended / Pointing Up
            else:
                fingers_open.append(0)  # Closed / Curled Down

        raw_gesture = "Unknown"

        # Core Standard States
        if fingers_open == [1, 1, 1, 1, 1]:
            raw_gesture = "Open Palm"
        elif fingers_open == [0, 1, 1, 0, 0] or fingers_open == [1, 1, 1, 0, 0]:
            raw_gesture = "Peace Sign"
        elif fingers_open == [1, 0, 0, 0, 0]:
            raw_gesture = "Thumbs Up"
        elif fingers_open == [0, 0, 0, 0, 0]:
            raw_gesture = "Fist"
        elif fingers_open == [0, 1, 0, 0, 1]:
            raw_gesture = "Rock On / Mute Toggle"
        elif fingers_open == [0, 1, 0, 0, 0]:
            if landmarks[8][1] < landmarks[6][1]:
                raw_gesture = "Point Up (Vol Up)"
            else:
                raw_gesture = "Point Down (Vol Down)"

        return raw_gesture, fingers_open

    def update_state(self, landmarks):
        raw_gesture, fingers_open = self.classify(landmarks)
        if raw_gesture == self.candidate_gesture:
            self.candidate_counter += 1
        else:
            self.candidate_gesture = raw_gesture
            self.candidate_counter = 1

        if self.candidate_counter >= self.debounce_frames:
            self.current_stable_gesture = self.candidate_gesture

        return self.current_stable_gesture, fingers_open
