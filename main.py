# main.py
import cv2
import time
import sys
import os

# Ensure the framework path checks remain invariant
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from detector import HandDetector
from gestures import GestureClassifier
from system_controller import SystemActionController


def draw_dashboard(frame, gesture, action, locked_status, cooldown_left, fps):
    """
    Renders a highly professional, semi-transparent Telemetry Dashboard HUD
    directly onto the video matrix screen to display core system states.
    """
    h, w, _ = frame.shape

    # Define our HUD boundary block coordinates (Top Right Panel)
    hud_x1, hud_y1 = w - 340, 15
    hud_x2, hud_y2 = w - 15, 185

    # 1. Render a semi-transparent dark-mode dashboard backdrop panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (20, 20, 20), -1)

    # Dynamic alpha-blend to achieve a clean glass-overlay UI look
    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Draw a clean border outline vector around our panel overlay canvas
    cv2.rectangle(frame, (hud_x1, hud_y1), (hud_x2, hud_y2), (80, 80, 80), 1)

    # 2. Map structural system text readouts onto our dashboard layout
    cv2.putText(
        frame,
        "SYSTEM INTEGRATION ENGINE",
        (hud_x1 + 15, hud_y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
    )

    # Safety Control Lock Indicator State
    lock_text = "SECURE / LOCKED" if locked_status else "ACTIVE / OPERATIONAL"
    lock_color = (0, 0, 255) if locked_status else (0, 255, 0)
    cv2.putText(
        frame,
        f"Safety Status: {lock_text}",
        (hud_x1 + 15, hud_y1 + 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        lock_color,
        1,
    )

    # Hand Core Stable Input Telemetry State
    cv2.putText(
        frame,
        f"Stabilized Input: {gesture}",
        (hud_x1 + 15, hud_y1 + 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        1,
    )

    # Operating System Action Macro Execution Status State
    cv2.putText(
        frame,
        f"Executed Macro: {action}",
        (hud_x1 + 15, hud_y1 + 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 150, 0),
        1,
    )

    # Temporal Cooldown Progress State Bar Metrics
    cd_string = (
        f"{max(0.0, cooldown_left):.1f}s Locked"
        if cooldown_left > 0
        else "READY TO TRIGGER"
    )
    cd_color = (100, 100, 255) if cooldown_left > 0 else (0, 255, 0)
    cv2.putText(
        frame,
        f"Macro Cooldown: {cd_string}",
        (hud_x1 + 15, hud_y1 + 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        cd_color,
        1,
    )

    # Performance metric loop index readout counter
    cv2.putText(
        frame,
        f"Performance Loop: {int(fps)} FPS",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
    )


def main():
    cap = cv2.VideoCapture(0)

    # Initialize our highly optimized modular processing engine suite
    detector = HandDetector()
    classifier = GestureClassifier(
        debounce_frames=12
    )  # High filter debounce value for safety
    controller = SystemActionController(
        action_cooldown=1.8
    )  # 1.8 seconds hardware cool window

    prev_time = 0
    current_action = "None"

    print("\n=======================================================")
    print("AI SYSTEM INTEGRATION CONTROL HUB ENGINE INITIALIZED")
    print("=======================================================")
    print("• Hold up a FIST for 1.5 seconds to Toggle System Lock/Unlock.")
    print("• Hold up an OPEN PALM to dynamically Scroll Windows Up.")
    print("• Hold up a PEACE SIGN to emit a system Media Play/Pause command.")
    print("• Hold up a THUMBS UP to trigger an Alt+Tab App Switch sequence.")
    print("• Press 'q' within the dashboard screen console matrix to terminate.")
    print("=======================================================\n")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)

        # 1. Core Hand Mesh landmark ingestion sequence
        frame, landmarks = detector.process_frame(frame)

        # 2. Evaluate spatial landmarks through our state debouncing filter block
        gesture, _ = classifier.update_state(landmarks)

        # 3. Process execution outputs based on temporal logic parameters
        action_status, time_since_last = controller.execute_action(gesture)

        # Clean up text feedback behaviors for UI clarity
        if action_status not in ["COOLDOWN ACTIVE", "SYSTEM LOCKED"]:
            current_action = action_status
        elif gesture == "No Hand Detected" and action_status != "SYSTEM LOCKED":
            current_action = "None"

        # 4. Calculate the real-time cooldown clock metrics
        cooldown_left = controller.action_cooldown - time_since_last
        if controller.system_locked:
            cooldown_left = 0.0

        # 5. Measure loop frequencies metrics
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # 6. Render the telemetry overlay engine panel framework visually
        draw_dashboard(
            frame, gesture, current_action, controller.system_locked, cooldown_left, fps
        )

        cv2.imshow("AI Gesture-Driven Reaction Engine Dashboard", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
