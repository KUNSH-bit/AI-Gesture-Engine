# gestures.py
import numpy as np


class GestureClassifier:
    def __init__(self, debounce_frames=8):
        self.TIP_IDS = [4, 8, 12, 16, 20]
        self.debounce_frames = debounce_frames

        # Temporal persistence tracking parameters
        self.current_stable_gesture = "Neutral Mode"
        self.candidate_gesture = "Neutral Mode"
        self.candidate_counter = 0

    def classify(self, landmarks):
        """
        Evaluates scale-normalized matrices using strict structural guards.
        Returns an explicit 'Neutral Mode' if input configurations match no macros.
        """
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", []

        fingers_open = []

        # 1. INVARIANT THUMB DISTANCE: Measured using scale-normalized vectors
        thumb_tip = landmarks[4]
        index_base = landmarks[5]
        thumb_to_index_dist = np.linalg.norm(thumb_tip - index_base)

        # Since landmarks are perfectly normalized by hand size, thresholds are fixed constants
        if thumb_to_index_dist > 0.65:
            fingers_open.append(1)  # Extended
        else:
            fingers_open.append(0)  # Closed

        # 2. FINGER HEIGHT CHECKS: (Y-axis coordinate comparisons)
        for i in range(1, 5):
            tip_idx = self.TIP_IDS[i]
            pip_idx = tip_idx - 2
            if landmarks[tip_idx][1] < landmarks[pip_idx][1]:
                fingers_open.append(1)  # Open
            else:
                fingers_open.append(0)  # Closed

        # 3. SAFETY COMMAND MAPPING DICTIONARY MATRIX
        # Explicitly falls back to "Neutral Mode" when patterns deviate
        raw_gesture = "Neutral Mode"

        if fingers_open == [1, 1, 1, 1, 1]:
            raw_gesture = "Open Palm (Scroll)"
        elif fingers_open == [0, 1, 1, 0, 0]:
            raw_gesture = "Peace Sign (Play/Pause)"
        elif fingers_open == [0, 0, 0, 0, 0]:
            raw_gesture = "Fist (Toggle Lock)"
        elif fingers_open == [1, 1, 0, 0, 0]:
            # Left Click Trigger check: Thumb is pinched down closely while Index is open
            if thumb_to_index_dist < 0.35:
                raw_gesture = "Left Click Triggered"
            else:
                raw_gesture = "Mouse Navigation Mode"

        return raw_gesture, fingers_open

    def update_state(self, landmarks):
        """
        Temporal state-machine debouncer logic blocks.
        Requires a gesture to be recognized consistently across multiple frames.
        """
        raw_gesture, fingers_open = self.classify(landmarks)

        if raw_gesture == self.candidate_gesture:
            self.candidate_counter += 1
        else:
            self.candidate_gesture = raw_gesture
            self.candidate_counter = 1

        # Commit state updates only when persistence validation passes target window
        if self.candidate_counter >= self.debounce_frames:
            self.current_stable_gesture = self.candidate_gesture

        return self.current_stable_gesture, fingers_open
