# system_controller.py
import pyautogui
import time


# Disable PyAutoGUI fail-safe movements to ensure smooth background macro executions
pyautogui.FAILSAFE = False


class SystemActionController:
    def __init__(self, action_cooldown=1.5):
        self.action_cooldown = action_cooldown
        self.last_action_time = 0
        self.system_locked = False

    def execute_action(self, gesture):
        """
        Evaluates safety rules, checks hardware cooldown timers, and
        transmits macro instructions straight to the Operating System kernel.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_action_time

        # 1. Global Safety Control: System Lock Toggle via 'Fist'
        if gesture == "Fist":
            if time_since_last > self.action_cooldown:
                self.system_locked = not self.system_locked
                self.last_action_time = current_time
                print(
                    f"[SYSTEM CONTROL] - Safety Toggle Activated. Locked Status: {self.system_locked}"
                )
            return "TOGGLE LOCK", time_since_last

        # If the system is explicitly locked down by safety parameters, drop execution
        if self.system_locked:
            return "SYSTEM LOCKED", time_since_last

        # 2. Safety Control: Check Cooldown Window Matrix
        if time_since_last < self.action_cooldown:
            return "COOLDOWN ACTIVE", time_since_last

        # 3. Gesture-to-Action Mapping Suite
        action_triggered = "None"

        if gesture == "Peace Sign":
            # Universal Operating System Play/Pause media toggle key
            pyautogui.press("playpause")
            action_triggered = "Media Play/Pause"
            self.last_action_time = current_time

        elif gesture == "Thumbs Up":
            # Trigger OS App Switching Engine Hotkey (Alt + Tab loop)
            pyautogui.hotkey("alt", "tab")
            action_triggered = "Switch Window (Alt+Tab)"
            self.last_action_time = current_time

        elif gesture == "Open Palm":
            # Execute an upward scroll context sequence
            pyautogui.scroll(300)
            action_triggered = "Scroll Up Window"
            # Lower cooldown target specifically for scrolling fluidity
            self.last_action_time = current_time - (self.action_cooldown - 0.2)

        return action_triggered, time_since_last
