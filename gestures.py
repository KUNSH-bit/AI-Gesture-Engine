# gestures.py
class GestureClassifier:
    def __init__(self, debounce_frames=10):
        # MediaPipe landmark indices for the structural tips of the 5 fingers
        self.TIP_IDS = [4, 8, 12, 16, 20]

        # Debouncing variables to manage state history across processing ticks
        self.debounce_frames = debounce_frames
        self.current_stable_gesture = "No Hand Detected"
        self.candidate_gesture = "No Hand Detected"
        self.candidate_counter = 0

    def classify(self, landmarks):
        """
        Analyzes normalized spatial coordinate locations to classify raw hand orientations.
        """
        if landmarks is None or len(landmarks) < 21:
            return "No Hand Detected", [0, 0, 0, 0, 0]

        fingers_open = []

        # 1. THUMB AXIS LOGIC: Check horizontal displacement relative to its base joint
        if landmarks[4][0] > landmarks[2][0]:
            fingers_open.append(1)  # Extended
        else:
            fingers_open.append(0)  # Closed

        # 2. FLUID FINGERS MATRIX: Check vertical tip coordinates against knuckles bases
        for i in range(1, 5):
            tip_idx = self.TIP_IDS[i]
            pip_idx = tip_idx - 2

            if landmarks[tip_idx][1] < landmarks[pip_idx][1]:
                fingers_open.append(1)  # Extended / Pointing Up
            else:
                fingers_open.append(0)  # Closed / Curled Down

        # 3. GESTURE TRANSLATION ARRAY LOOKUPS
        raw_gesture = "Unknown"

        if fingers_open == [1, 1, 1, 1, 1]:
            raw_gesture = "Open Palm"
        elif fingers_open == [0, 1, 1, 0, 0] or fingers_open == [1, 1, 1, 0, 0]:
            raw_gesture = "Peace Sign"
        elif fingers_open == [1, 0, 0, 0, 0] and landmarks[4][1] < landmarks[3][1]:
            raw_gesture = "Thumbs Up"
        elif fingers_open == [0, 0, 0, 0, 0]:
            raw_gesture = "Fist"
        elif fingers_open == [0, 1, 0, 0, 0]:
            raw_gesture = "Point"

        return raw_gesture, fingers_open

    def update_state(self, landmarks):
        """
        Filters raw structural states through a consecutive frame threshold filter window
        to ensure zero label flickering on live video matrices.
        """
        raw_gesture, fingers_open = self.classify(landmarks)

        # If input gesture matches our current tracking state candidate, step up counter
        if raw_gesture == self.candidate_gesture:
            self.candidate_counter += 1
        else:
            # If state shift happens, initialize tracing metrics for the new variant
            self.candidate_gesture = raw_gesture
            self.candidate_counter = 1

        # Push to absolute stable configuration only if candidate survives target windows
        if self.candidate_counter >= self.debounce_frames:
            self.current_stable_gesture = self.candidate_gesture

        return self.current_stable_gesture, fingers_open
