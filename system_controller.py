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
        self.media_triggered = False

        # State parameters to separate clicking from dragging actions
        self.drag_mode_engaged = False
        self.thumb_was_pressed = False
        self.start_x, self.start_y = 0, 0
        self.press_start_time = 0

    def execute_action(self, gesture, raw_landmarks=None):
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        if gesture != "Peace Sign (Play/Pause)":
            self.media_triggered = False

        # 1. CLEAN CLICK UP / DROP SYSTEM OVERRIDES
        if gesture != "Air Drag Active" and self.thumb_was_pressed:
            if self.drag_mode_engaged:
                # If we were dragging, release the mouse down lock state safely
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                self.drag_mode_engaged = False
                print("[MOUSE SYSTEM] - Air Drag Dropped.")
            else:
                # If hand movement stayed inside buffer window, trigger a fast Single Click tap
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.01)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print("[MOUSE SYSTEM] - Fast Single Click Executed.")

            self.thumb_was_pressed = False

        if gesture == "Fist (Toggle Lock)":
            if time_since_last > self.action_cooldown:
                self.system_locked = not self.system_locked
                self.last_action_time = current_time
            return "TOGGLE LOCK", time_since_last

        if self.system_locked:
            return "SYSTEM LOCKED", time_since_last

        action_triggered = "Tracking Pointer"

        # 2. FIXED SCROLLING DICTIONARY MAPS
        scroll_gestures = {
            "Open Palm (Scroll Up)": (win32con.MOUSEEVENTF_WHEEL, 150),
            "Open Palm (Scroll Down)": (win32con.MOUSEEVENTF_WHEEL, -150),
            "Rock Sign (Scroll Down)": (
                win32con.MOUSEEVENTF_WHEEL,
                -150,
            ),  # Back to matching scroll down
        }

        if gesture in scroll_gestures:
            if current_time - self.last_scroll_time >= 0.05:
                event_type, delta = scroll_gestures[gesture]
                try:
                    mx, my = win32api.GetCursorPos()
                    win32api.mouse_event(event_type, mx, my, delta, 0)
                    self.last_scroll_time = current_time
                    return f"SCROLL ACTIVE: {gesture}", time_since_last
                except Exception as e:
                    print(f"Scrolling error: {e}")
                    return "SCROLL ERROR", time_since_last
            return "SCROLL WAITING", time_since_last

        # 3. HIGH-PRECISION SEPARATED CURSOR NAVIGATION PIPELINE
        if (
            (gesture in ["Mouse Navigation Mode", "Air Drag Active"])
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

            # Execute cursor update shifts
            pyautogui.moveTo(int(curr_x), int(curr_y))
            self.prev_x, self.prev_y = float(curr_x), float(curr_y)
            action_triggered = "Cursor Active"

            # Smart Spatial Selection Buffer Engine
            if gesture == "Air Drag Active":
                if not self.thumb_was_pressed:
                    # Ingest initial position anchors when thumb pulls close
                    self.start_x, self.start_y = curr_x, curr_y
                    self.thumb_was_pressed = True
                    self.press_start_time = current_time
                    action_triggered = "Click Input Initialized"
                else:
                    # Calculate tracking distance moved since thumb first closed
                    distance_moved = np.sqrt(
                        (curr_x - self.start_x) ** 2 + (curr_y - self.start_y) ** 2
                    )

                    # Engage dragging down event ONLY if index travels past a 25-pixel buffer window
                    if not self.drag_mode_engaged and distance_moved > 25:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        self.drag_mode_engaged = True
                        print("[MOUSE SYSTEM] - Drag Click Lock Engaged.")

                    if self.drag_mode_engaged:
                        action_triggered = "DRAGGING ASSET..."
                    else:
                        action_triggered = "PREPARED TO CLICK / TAP"

            return action_triggered, time_since_last

        # 4. DISCRETE MEDIA MACROS
        if gesture == "Peace Sign (Play/Pause)":
            if not self.media_triggered:
                pyautogui.press("playpause")
                self.media_triggered = True
                self.last_action_time = current_time
                return "Media Play/Pause Activated", time_since_last
            else:
                return "Media Macro Locked", time_since_last

        return action_triggered, time_since_last
