# system_controller.py
import pyautogui
import time
import numpy as np
import win32api
import win32con

pyautogui.FAILSAFE = False


class SystemActionController:
    def __init__(self, action_cooldown=1.0):
        self.action_cooldown = action_cooldown
        self.last_action_time = 0
        self.system_locked = False

        self.screen_width, self.screen_height = pyautogui.size()
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 4

        self.last_scroll_time = 0

    def execute_action(self, gesture, raw_landmarks=None):
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        if gesture == "Fist (Toggle Lock)":
            if time_since_last > self.action_cooldown:
                self.system_locked = not self.system_locked
                self.last_action_time = current_time
            return "TOGGLE LOCK", time_since_last

        if self.system_locked:
            return "SYSTEM LOCKED", time_since_last

        action_triggered = "Tracking Pointer"

        # 1. FIX: CONTINUOUS WINDOWS MOUSE-WHEEL SCROLLING WITH ACTIVE POSITION HOOKS
        scroll_gestures = {
            "Open Palm (Scroll Up)": 150,
            "Open Palm (Scroll Down)": -150,
        }

        if gesture in scroll_gestures:
            if current_time - self.last_scroll_time >= 0.05:
                delta = scroll_gestures[gesture]
                try:
                    # Dynamically capture where the mouse is sitting right now
                    mx, my = win32api.GetCursorPos()

                    # Pass the active screen coordinates instead of raw 0, 0
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, mx, my, delta, 0)
                    self.last_scroll_time = current_time
                    direction = "UP" if delta > 0 else "DOWN"
                    return f"SCROLLING {direction}", time_since_last
                except Exception as e:
                    print(f"Scrolling error: {e}")
                    return "SCROLL ERROR", time_since_last
            return "SCROLL WAITING", time_since_last

        # 2. LIVE AIR-MOUSE NAVIGATION & PRECISION CLICK PIPELINE
        if (
            (gesture in ["Mouse Navigation Mode", "Left Click Triggered"])
            and raw_landmarks is not None
            and len(raw_landmarks) >= 21
        ):
            index_x = float(raw_landmarks[8][0])
            index_y = float(raw_landmarks[8][1])

            pad = 0.15
            target_x = np.interp(index_x, [pad, 1.0 - pad], [0, self.screen_width])
            target_y = np.interp(index_y, [pad, 1.0 - pad], [0, self.screen_height])

            curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothening
            curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothening

            pyautogui.moveTo(int(curr_x), int(curr_y))
            self.prev_x, self.prev_y = float(curr_x), float(curr_y)
            action_triggered = "Cursor Active"

            if gesture == "Left Click Triggered":
                if time_since_last > 0.5:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.01)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    action_triggered = "OS LEFT CLICK EXECUTED"
                    self.last_action_time = current_time
                return action_triggered, (current_time - self.last_action_time)

            return action_triggered, (current_time - self.last_action_time)

        # 3. GLOBAL DISCRETE MEDIA HOTKEYS MACROS
        if time_since_last < self.action_cooldown:
            return "COOLDOWN ACTIVE", time_since_last

        if gesture == "Peace Sign (Play/Pause)":
            pyautogui.press("playpause")
            action_triggered = "Media Play/Pause"
            self.last_action_time = current_time

        return action_triggered, time_since_last
