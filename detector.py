# detector.py
import cv2
import mediapipe as mp
import numpy as np
import os


class HandDetector:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        self.HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        model_path = os.path.abspath("hand_landmarker.task")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"[CRITICAL ERROR] 'hand_landmarker.task' missing at: {model_path}"
            )

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = self.HandLandmarker.create_from_options(options)
        self.frame_timestamp_ms = 0

    def process_frame(self, frame):
        """
        Flips the frame matrix for natural mirror viewing, extracts landmarks,
        and computes normalized scale-invariant and raw tracking arrays.
        """
        # 1. Flip the video frame horizontally for natural mirrored interaction
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        self.frame_timestamp_ms += 33
        result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)

        normalized_landmarks = None
        raw_landmarks = None

        if result.hand_landmarks:
            hand_pts = result.hand_landmarks[0]

            points = []
            for lm in hand_pts:
                pt_x = int(lm.x * w)
                pt_y = int(lm.y * h)
                # Draw green tracking skeleton points onto our mirrored frame canvas
                cv2.circle(frame, (pt_x, pt_y), 4, (0, 255, 0), -1)
                points.append([lm.x, lm.y, lm.z])

            raw_landmarks = np.array(points)
            if len(raw_landmarks) >= 21:
                # Center coordinates relative to the wrist (Landmark 0)
                translated = raw_landmarks - raw_landmarks[0, :]

                # Dynamic scale vector mapping using Wrist (0) to Middle Finger Knuckle (9) distance
                hand_scale = np.linalg.norm(translated[9] - translated[0])
                if hand_scale > 0:
                    normalized_landmarks = translated / hand_scale
                else:
                    normalized_landmarks = translated

        return frame, normalized_landmarks, raw_landmarks
