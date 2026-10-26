import pyautogui
import time

pyautogui.FAILSAFE = False


class SystemActionController:
    def __init__(self, action_cooldown=1.2):
        self.action_cooldown = action_cooldown
        self.last_action_time = 0
        self.system_locked = False

    def execute_action(self, gesture):
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        if gesture == "Fist":
            if time_since_last > self.action_cooldown:
                self.system_locked = not self.system_locked
                self.last_action_time = current_time
            return "TOGGLE LOCK", time_since_last

        if self.system_locked:
            return "SYSTEM LOCKED", time_since_last

        action_triggered = "None"

        if gesture == "Point Up (Vol Up)":
            pyautogui.press("volumeup")
            action_triggered = "Volume Increased (+)"
            self.last_action_time = current_time - (self.action_cooldown - 0.15)
            return action_triggered, (current_time - self.last_action_time)

        elif gesture == "Point Down (Vol Down)":
            pyautogui.press("volumedown")
            action_triggered = "Volume Decreased (-)"
            self.last_action_time = current_time - (self.action_cooldown - 0.15)
            return action_triggered, (current_time - self.last_action_time)

        elif gesture == "Open Palm":
            pyautogui.scroll(250)
            action_triggered = "Scroll Up Window"
            self.last_action_time = current_time - (self.action_cooldown - 0.25)
            return action_triggered, (current_time - self.last_action_time)

        if time_since_last < self.action_cooldown:
            return "COOLDOWN ACTIVE", time_since_last

        if gesture == "Peace Sign":
            pyautogui.press("playpause")
            action_triggered = "Media Play/Pause"
            self.last_action_time = current_time

        elif gesture == "Thumbs Up":
            pyautogui.hotkey("alt", "tab")
            action_triggered = "Switch Window (Alt+Tab)"
            self.last_action_time = current_time

        elif gesture == "Rock On / Mute Toggle":
            pyautogui.press("volumemute")
            action_triggered = "Audio Mute/Unmute"
            self.last_action_time = current_time

        return action_triggered, time_since_last
