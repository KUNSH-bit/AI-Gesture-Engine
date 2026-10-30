import cv2
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from detector import HandDetector
from gestures import GestureClassifier
from system_controller import SystemActionController


def draw_dashboard(frame, gesture, action, locked_status, fist_frames, fps):
    h, w, _ = frame.shape
    hud_x1, hud_y1 = w - 360, 15
    hud_x2, hud_y2 = w - 15, 165

    overlay = frame.copy()
    cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (15, 15, 15), -1)
    alpha = 0.8
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (hud_x1, hud_y1), (hud_x2, hud_y2), (70, 70, 70), 1)

    cv2.putText(
        frame,
        "TOUCHLESS AIR-MOUSE CONTROL HUB",
        (hud_x1 + 15, hud_y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        2,
    )

    lock_text = "SYSTEM DISABLED / LOCKED" if locked_status else "AIR-MOUSE OPERATIONAL"
    lock_color = (0, 0, 255) if locked_status else (0, 255, 0)
    cv2.putText(
        frame,
        f"Status: {lock_text}",
        (hud_x1 + 15, hud_y1 + 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        lock_color,
        1,
    )

    if gesture == "HOLDING FIST TO LOCK...":
        progress = int((fist_frames / 90) * 100)
        cv2.putText(
            frame,
            f"Locking Progress: {progress}%",
            (hud_x1 + 15, hud_y1 + 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (100, 100, 255),
            1,
        )
    else:
        cv2.putText(
            frame,
            f"Gesture Shape: {gesture}",
            (hud_x1 + 15, hud_y1 + 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 255),
            1,
        )

    cv2.putText(
        frame,
        f"OS Output: {action[:28]}",
        (hud_x1 + 15, hud_y1 + 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 150, 0),
        1,
    )

    cv2.putText(
        frame,
        "3s Fist=Lock | Pinch=Click | Open Hand=Scroll",
        (hud_x1 + 15, hud_y1 + 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        (180, 180, 180),
        1,
    )

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
    detector = HandDetector()
    classifier = GestureClassifier(fps=30)
    controller = SystemActionController(action_cooldown=1.2)

    prev_time = 0
    current_action = "None"

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame, landmarks, raw_landmarks = detector.process_frame(frame)
        gesture, fist_frames = classifier.update_state(landmarks)

        action_status, _ = controller.execute_action(gesture, raw_landmarks)

        if gesture in ["No Hand Detected", "HOLDING FIST TO LOCK..."]:
            current_action = "None"
        else:
            current_action = action_status

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        draw_dashboard(
            frame, gesture, current_action, controller.system_locked, fist_frames, fps
        )
        cv2.imshow("AI Gesture-Driven Reaction Engine Dashboard", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
