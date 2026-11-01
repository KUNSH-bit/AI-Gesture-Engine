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

        # Thumb landmarks
        thumb_cmc = landmarks[1]
        thumb_mcp = landmarks[2]
        thumb_ip = landmarks[3]
        thumb_tip = landmarks[4]
        index_base = landmarks[5]

        thumb_to_index_dist = np.linalg.norm(thumb_tip - index_base)

        # Detect thumb extension using its joints
        thumb_length = np.linalg.norm(thumb_tip - thumb_mcp)

        thumb_vertical_extension = thumb_mcp[1] - thumb_tip[1]

        thumb_horizontal_extension = abs(thumb_tip[0] - thumb_mcp[0])

        # Thumb must be extended from its base
        thumb_extended = thumb_length > 0.12 and (
            thumb_vertical_extension > 0.10 or thumb_horizontal_extension > 0.16
        )

        # Thumb pointing upwards
        thumb_pointing_up = (
            thumb_tip[1] < thumb_ip[1] - 0.03
            and thumb_ip[1] < thumb_mcp[1]
            and thumb_vertical_extension > 0.12
        )

        # Thumb folded towards palm
        thumb_folded = thumb_to_index_dist < 0.36 and not thumb_pointing_up

        if thumb_folded:
            self.thumb_was_closed = True
        elif thumb_extended:
            self.thumb_was_closed = False

        # Existing finger detection
        index_open = landmarks[8][1] < landmarks[6][1]
        middle_open = landmarks[12][1] < landmarks[10][1]
        ring_open = landmarks[16][1] < landmarks[14][1]
        pinky_open = landmarks[20][1] < landmarks[18][1]

        index_down = landmarks[8][1] > landmarks[6][1] + 0.1
        middle_down = landmarks[12][1] > landmarks[10][1] + 0.1
        ring_down = landmarks[16][1] > landmarks[14][1] + 0.1
        pinky_down = landmarks[20][1] > landmarks[18][1] + 0.1

        other_fingers_curled = not (
            index_open or middle_open or ring_open or pinky_open
        )

        is_fist = other_fingers_curled and not thumb_pointing_up

        is_open_palm_up = index_open and middle_open and ring_open and pinky_open

        is_open_palm_down = index_down and middle_down and ring_down and pinky_down

        raw_gesture = "Neutral Mode"

        # Improved thumbs-up detection
        if other_fingers_curled and thumb_pointing_up and thumb_extended:
            # Preserve directional switching logic
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
