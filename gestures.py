import numpy as np


class GestureClassifier:
    def __init__(self, fps=30):
        self.TIP_IDS = [4, 8, 12, 16, 20]

        self.lock_threshold_frames = int(3.0 * fps)
        self.fist_counter = 0

        self.debounce_frames = 2
        self.current_stable_gesture = "Neutral Mode"
        self.candidate_gesture = "Neutral Mode"
        self.candidate_counter = 0

        self.thumb_was_closed = False

    def classify(self, landmarks):
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", 0.0

        thumb_tip = landmarks[4]
        index_base = landmarks[5]
        thumb_to_index_dist = np.linalg.norm(thumb_tip - index_base)

        if thumb_to_index_dist < 0.36:
            self.thumb_was_closed = True
        elif thumb_to_index_dist > 0.48:
            self.thumb_was_closed = False

        index_open = landmarks[8][1] < landmarks[6][1]
        middle_open = landmarks[12][1] < landmarks[10][1]
        ring_open = landmarks[16][1] < landmarks[14][1]
        pinky_open = landmarks[20][1] < landmarks[18][1]

        index_down = landmarks[8][1] > landmarks[6][1] + 0.1
        middle_down = landmarks[12][1] > landmarks[10][1] + 0.1
        ring_down = landmarks[16][1] > landmarks[14][1] + 0.1
        pinky_down = landmarks[20][1] > landmarks[18][1] + 0.1

        is_fist = not (index_open or middle_open or ring_open or pinky_open)
        is_open_palm_up = index_open and middle_open and ring_open and pinky_open
        is_open_palm_down = index_down and middle_down and ring_down and pinky_down

        raw_gesture = "Neutral Mode"

        if (
            not (index_open or middle_open or ring_open or pinky_open)
            and thumb_to_index_dist > 0.38
        ):
            if landmarks[4][0] < -0.12:
                raw_gesture = "Thumbs Up (Switch Right)"
            elif landmarks[4][0] > 0.12:
                raw_gesture = "Thumbs Up (Switch Left)"
            else:
                raw_gesture = "Thumbs Up (Menu Hold)"

        elif is_fist:
            raw_gesture = "Fist Shape Detected"
        elif is_open_palm_up:
            raw_gesture = "Open Palm (Scroll Up)"
        elif is_open_palm_down:
            raw_gesture = "Open Palm (Scroll Down)"
        elif index_open and pinky_open and not (middle_open or ring_open):
            raw_gesture = "Rock Sign (Scroll Down)"
        elif index_open and middle_open and not (ring_open or pinky_open):
            raw_gesture = "Peace Sign (Play/Pause)"
        elif index_open and not (middle_open or ring_open or pinky_open):
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
