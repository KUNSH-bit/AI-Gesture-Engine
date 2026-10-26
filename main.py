# main.py
import cv2
import time

# Direct imports from the same directory level
from detector import HandDetector
from gestures import GestureClassifier


def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    classifier = GestureClassifier()

    prev_time = 0

    print("AI Gesture Engine with Classifiers Initialized. Press 'q' to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame, landmarks = detector.process_frame(frame)

        # Run classification through our temporal state engine filter
        if landmarks is not None:
            gesture, debug_info = classifier.update_state(landmarks)

            # Print the classified text cleanly onto the top of the application frame
            cv2.putText(
                frame,
                f"GESTURE: {gesture}",
                (10, 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (0, 255, 255),
                2,
            )

            # Draw the finger state bit array underneath for judge inspection
            cv2.putText(
                frame,
                f"Vector State: {debug_info}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
            )
        else:
            cv2.putText(
                frame,
                "GESTURE: No Hand Present",
                (10, 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (0, 0, 255),
                2,
            )

        # System Frame Rate Counter
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            1,
        )

        cv2.imshow("AI Gesture-Driven Reaction Engine Dashboard", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
