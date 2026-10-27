# system_controller.py
import pyautogui
import time
import numpy as np

pyautogui.FAILSAFE = False


class SystemActionController:
    def __init__(self, action_cooldown=1.0):
        self.action_cooldown = action_cooldown
        self.last_action_time = 0
        self.system_locked = False

        # Get primary screen aspect layout dimensions
        self.screen_width, self.screen_height = pyautogui.size()

        # Tracking states for spatial smoothing filters
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 4

    def execute_action(self, gesture, raw_landmarks=None):
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        # Global Safety Toggle Override Lock remains highest priority
        if gesture == "Fist (Toggle Lock)":
            if time_since_last > self.action_cooldown:
                self.system_locked = not self.system_locked
                self.last_action_time = current_time
            return "TOGGLE LOCK", time_since_last

        if self.system_locked:
            return "SYSTEM LOCKED", time_since_last

        action_triggered = "Tracking Pointer"

        # 1. LIVE MOUSE NAVIGATION PIPELINE
        if (
            gesture in ["Mouse Navigation Mode", "Left Click Triggered"]
        ) and raw_landmarks is not None:
            # Extract raw coordinate fractions of the index finger tip (Index 8)
            # MediaPipe yields values from 0.0 to 1.0 relative to camera bounds
            index_x = raw_landmarks[8][0]
            index_y = raw_landmarks[8][1]

            # Map camera frame window coordinates to absolute display monitor resolutions
            # Create a 20% inner bounding padding box to make reaching corners easier
            pad = 0.2
            target_x = np.interp(index_x, [pad, 1.0 - pad], [0, self.screen_width])
            target_y = np.interp(index_y, [pad, 1.0 - pad], [0, self.screen_height])

            # Apply Exponential Smooth Filter (Linear Interpolation) to eliminate hand micro-shaking
            curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothening
            curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothening

            # Command OS cursor position updating shifts
            pyautogui.moveTo(int(curr_x), int(curr_y))
            self.prev_x, self.prev_y = curr_x, curr_y
            action_triggered = f"Cursor Moving to [{int(curr_x)}, {int(curr_y)}]"

            # Handle Click State Triggers instantly
            if gesture == "Left Click Triggered" and time_since_last > 0.4:
                pyautogui.click()
                action_triggered = "OS LEFT CLICK EXECUTED"
                self.last_action_time = current_time

            return action_triggered, (current_time - self.last_action_time)

        # 2. DISCRETE MACROS
        if time_since_last < self.action_cooldown:
            return "COOLDOWN ACTIVE", time_since_last

        if gesture == "Open Palm (Scroll)":
            pyautogui.scroll(200)
            action_triggered = "Scroll Window Up"
        elif gesture == "Peace Sign (Play/Pause)":
            pyautogui.press("playpause")
            action_triggered = "Media Play/Pause"
            self.last_action_time = current_time

        return action_triggered, time_since_last
