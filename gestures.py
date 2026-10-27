# gestures.py
import numpy as np


class GestureClassifier:
    def __init__(self, fps=30):
        self.TIP_IDS = [4, 8, 12, 16, 20]

        # 3-Second Lock Configuration parameters
        self.lock_threshold_frames = int(3.0 * fps)
        self.fist_counter = 0

        self.debounce_frames = 2
        self.current_stable_gesture = "Neutral Mode"
        self.candidate_gesture = "Neutral Mode"
        self.candidate_counter = 0

        # Hysteresis memory flag to track the thumb state smoothly
        self.thumb_was_closed = False

    def classify(self, landmarks):
        """
        Processes normalized matrices to classify directional hand orientations.
        Uses dual-threshold maps to track thumb profiles cleanly.
        """
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", 0.0

        # 1. MEASURE THUMB TIP (4) TO INDEX BASE (5) SCALE DISTANCE
        thumb_tip = landmarks[4]
        index_base = landmarks[5]
        thumb_to_index_dist = np.linalg.norm(thumb_tip - index_base)

        # 2. HYSTERESIS FILTER: Check thumb extension state using dual boundaries
        if thumb_to_index_dist < 0.36:
            self.thumb_was_closed = True
        elif thumb_to_index_dist > 0.48:
            self.thumb_was_closed = False

        # 3. EXTENSION PROFILES ON THE Y-AXIS (Index 1)
        index_up = landmarks[8][1] < landmarks[6][1]
        middle_up = landmarks[12][1] < landmarks[10][1]
        ring_up = landmarks[16][1] < landmarks[14][1]
        pinky_up = landmarks[20][1] < landmarks[18][1]

        # Inverted downward extensions metrics
        index_down = landmarks[8][1] > landmarks[6][1] + 0.1
        middle_down = landmarks[12][1] > landmarks[10][1] + 0.1
        ring_down = landmarks[16][1] > landmarks[14][1] + 0.1
        pinky_down = landmarks[20][1] > landmarks[18][1] + 0.1

        is_fist = not (index_up or middle_up or ring_up or pinky_up)
        is_open_palm_up = index_up and middle_up and ring_up and pinky_up
        is_open_palm_down = index_down and middle_down and ring_down and pinky_down

        # 4. DECISION TREE MAPPING LAYER
        raw_gesture = "Neutral Mode"

        if is_fist:
            raw_gesture = "Fist Shape Detected"
        elif is_open_palm_up:
            raw_gesture = "Open Palm (Scroll Up)"
        elif is_open_palm_down:
            raw_gesture = "Open Palm (Scroll Down)"
        # REVERTED INTERFACE FIX: Rock Sign maps exclusively to Scroll Down
        elif index_up and pinky_up and not (middle_up or ring_up):
            raw_gesture = "Rock Sign (Scroll Down)"
        elif index_up and middle_up and not (ring_up or pinky_up):
            raw_gesture = "Peace Sign (Play/Pause)"
        elif index_up and not (middle_up or ring_up or pinky_up):
            if self.thumb_was_closed:
                raw_gesture = "Air Drag Active"
            else:
                raw_gesture = "Mouse Navigation Mode"

        return raw_gesture, thumb_to_index_dist

    def update_state(self, landmarks):
        raw_gesture, thumb_dist = self.classify(landmarks)

        if raw_gesture == "Fist Shape Detected":
            self.fist_counter += 1
            if self.fist_counter >= self.lock_threshold_frames:
                self.fist_counter = 0
                return "Fist (Toggle Lock)", self.fist_counter
            return "HOLDING FIST TO LOCK...", self.fist_counter
        else:
            self.fist_counter = 0

        if raw_gesture == self.candidate_gesture:
            self.candidate_counter += 1
        else:
            self.candidate_gesture = raw_gesture
            self.candidate_counter = 1

        if self.candidate_counter >= self.debounce_frames:
            self.current_stable_gesture = self.candidate_gesture

        return self.current_stable_gesture, self.fist_counter
