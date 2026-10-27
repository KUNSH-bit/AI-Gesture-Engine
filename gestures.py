# gestures.py
import numpy as np


class GestureClassifier:
    def __init__(self, fps=30):
        self.TIP_IDS = [4, 8, 12, 16, 20]

        # 3-Second Lock Configuration parameters
        self.lock_threshold_frames = int(3.0 * fps)
        self.fist_counter = 0

        # Debouncer window for fast inputs response loops
        self.debounce_frames = 2
        self.current_stable_gesture = "Neutral Mode"
        self.candidate_gesture = "Neutral Mode"
        self.candidate_counter = 0

    def classify(self, landmarks):
        """
        Processes normalized matrices to classify directional hand orientations.
        Provides robust scale-invariant tracking with widened thresholds for tight fists.
        """
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", 0.0

        # 1. TRACK FINGER CONFIGURATIONS ON THE Y-AXIS (Index 1)
        # We compare the Tip position to the middle joint (PIP) to see if it is extended upward
        index_up = landmarks[8][1] < landmarks[6][1]
        middle_up = landmarks[12][1] < landmarks[10][1]
        ring_up = landmarks[16][1] < landmarks[14][1]
        pinky_up = landmarks[20][1] < landmarks[18][1]

        # Check downward extensions profile tracking metrics
        index_down = landmarks[8][1] > landmarks[5][1] + 0.1
        middle_down = landmarks[12][1] > landmarks[9][1] + 0.1
        ring_down = landmarks[16][1] > landmarks[13][1] + 0.1
        pinky_down = landmarks[20][1] > landmarks[17][1] + 0.1

        # 2. MEASURE THUMB-TO-INDEX TIP GEOMETRIC PROXIMITY VECTOR DISTANCE
        thumb_tip = landmarks[4]
        index_base = landmarks[5]
        click_pinch_dist = np.linalg.norm(thumb_tip - index_base)

        # 3. EVALUATE PASSIVE PROFILE CONDITIONS MAPS
        # Widened check: A fist means no major fingers are pointing straight up or down
        is_fist = not (index_up or middle_up or ring_up or pinky_up)
        is_open_palm_up = index_up and middle_up and ring_up and pinky_up
        is_open_palm_down = index_down and middle_down and ring_down and pinky_down

        # 4. DECISION TREE RESOLUTION LAYER
        raw_gesture = "Neutral Mode"

        if is_fist:
            raw_gesture = "Fist Shape Detected"
        elif is_open_palm_up:
            raw_gesture = "Open Palm (Scroll Up)"
        elif is_open_palm_down:
            raw_gesture = "Open Palm (Scroll Down)"
        elif index_up and middle_up and not (ring_up or pinky_up):
            raw_gesture = "Peace Sign (Play/Pause)"
        elif index_up and not (middle_up or ring_up or pinky_up or index_down):
            if click_pinch_dist < 0.42:
                raw_gesture = "Left Click Triggered"
            else:
                raw_gesture = "Mouse Navigation Mode"

        return raw_gesture, click_pinch_dist

    def update_state(self, landmarks):
        raw_gesture, click_dist = self.classify(landmarks)

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
