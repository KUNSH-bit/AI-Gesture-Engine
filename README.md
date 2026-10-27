# AI Gesture Engine

### Real-Time Hand Gesture Recognition and Touchless Desktop Control

AI Gesture Engine is a Python-based computer vision project that transforms webcam input into hand gestures and maps recognized poses to desktop actions. It combines MediaPipe's pretrained hand-landmark detection model with a custom, rule-based gesture classifier to explore touchless human–computer interaction without specialized hardware or cloud inference.

The project brings together real-time hand tracking, geometric gesture recognition, temporal stabilization, and Windows desktop input control in a modular application.

## Overview

AI Gesture Engine follows a simple pipeline:

**Webcam → Hand Detection → Landmark Processing → Gesture Classification → Desktop Actions**

A webcam captures the user's hand, MediaPipe identifies 21 hand landmarks, and NumPy processes their coordinates. A custom classifier evaluates finger positions and produces gesture labels, which the system controller maps to mouse, scrolling, and media actions.

The application also displays a live dashboard with the recognized gesture, system status, action feedback, and approximate processing frame rate.

## Features

- **Real-Time Hand Tracking:** Detects a hand through a live webcam feed using MediaPipe Tasks.
- **21-Point Landmark Detection:** Processes three-dimensional hand landmark coordinates.
- **Geometric Gesture Recognition:** Classifies hand poses using manually defined landmark relationships rather than a custom-trained classifier.
- **Gesture Stabilization:** Uses consecutive-frame confirmation to reduce rapid changes in recognized gesture labels.
- **Touchless Mouse Control:** Moves the desktop cursor using the index fingertip's position.
- **Gesture-Based Clicking:** Triggers a left-click through the classifier's index-finger and thumb-proximity rule.
- **Scrolling:** Sends native Windows mouse-wheel events for recognized upward and downward finger orientations.
- **Media Controls:** Maps a sustained, recognized Peace Sign to the system's play/pause media command.
- **Timed System Lock:** Uses a fist-hold counter to toggle desktop-action control.
- **Live Debugging Dashboard:** Displays the gesture, action status, lock state, and approximate FPS.
- **Local Processing:** Performs hand detection and gesture classification locally.

## Supported Gestures and Actions

| Gesture | Intended action |
|---|---|
| Index finger and thumb extended | Cursor navigation |
| Index finger extended with thumb proximity to the hand | Left-click |
| Open Palm (Scroll Up) | Scroll upward |
| Rock Sign (Scroll Down) | Scroll downward |
| Peace Sign (Play/Pause) | Toggle media playback |
| Hold a fist for approximately 3 seconds | Toggle system-action lock |
| Thumbs Up | App Switcher |

The classifier also produces intermediate states, including `Neutral Mode`, `HOLDING FIST TO LOCK...`, and `No Hand Detected`.

**Note:** Gesture recognition is based on geometric rules. Scroll direction depends on the detected finger orientation, rather than tracking the palm's movement through space. Recognition and action reliability can vary with hand orientation, lighting, camera placement, and individual movement.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| OpenCV | Webcam capture, frame processing, and dashboard rendering |
| MediaPipe Tasks | Pretrained hand-landmark detection |
| NumPy | Landmark arrays and geometric calculations |
| PyAutoGUI | Cursor positioning and media-key input |
| PyWin32 | Windows mouse-wheel and mouse-button input |

## How It Works

### 1. Hand Landmark Detection

MediaPipe estimates 21 landmarks for a detected hand, including the wrist, finger joints, and fingertips. These coordinates provide the geometric information needed to recognize different poses.

### 2. Coordinate Processing

The detector creates wrist-relative coordinates by subtracting the wrist position from each landmark:

\[
P_i' = P_i-P_{\text{wrist}}
\]

It then scales these coordinates using the distance between the wrist and middle-finger knuckle. This reduces sensitivity to absolute hand position and some variations in hand size.

The detector also retains normalized image coordinates for cursor tracking.

### 3. Gesture Classification

The classifier compares fingertip positions with finger-joint positions and evaluates predefined geometric conditions.

The resulting labels are passed through a short consecutive-frame confirmation process to reduce rapid switching between gestures. Fist recognition also uses a frame counter to implement the timed lock gesture.

### 4. Desktop Action Execution

The system controller receives the recognized gesture and, where needed, the raw landmarks. It maps the gesture to the corresponding desktop operation.

Cursor coordinates are interpolated into screen coordinates and smoothed across frames. Scrolling uses Windows mouse-wheel events, while clicking and media playback use desktop input commands.

### 5. Live Feedback

OpenCV displays the camera feed with the detected hand skeleton, current gesture, action status, lock state, and approximate frame rate. This provides visual feedback for debugging the recognition and control pipeline.

## Getting Started

### Requirements

- Windows, for the current desktop-action implementation
- Python 3.10 or 3.11 recommended
- A working webcam
- Git and a terminal

### 1. Clone the repository

```bash
git clone https://github.com/KUNSH-bit/AI-Gesture-Engine.git
cd AI-Gesture-Engine
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python executable directly instead.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install opencv-python mediapipe numpy pyautogui pywin32
```

### 4. Run the application

Ensure `hand_landmarker.task` is present in the project root, then launch the application from that directory:

```bash
python main.py
```

The webcam dashboard should open and begin processing frames. Press `Q` while the dashboard is focused to close the application.

If the webcam fails to open, check camera permissions and ensure another application is not exclusively using it.

## Current Limitations

AI Gesture Engine is an evolving prototype, and several limitations remain:

- **Heuristic-based recognition:** The gesture classifier uses manually defined geometric conditions rather than a model trained on a custom gesture dataset.
- **Orientation sensitivity:** Finger-extension rules can behave differently as the hand rotates or changes position.
- **Threshold sensitivity:** The current geometric thresholds may require adjustment for different users and camera setups.
- **Limited gesture vocabulary:** Only predefined hand configurations and their associated actions are supported.
- **Windows-specific controls:** Desktop input injection uses PyWin32 and is not designed to work unchanged across operating systems.
- **No formal performance evaluation:** Recognition accuracy, false activations, and end-to-end action latency have not been established through a systematic benchmark.
- **Model-path dependency:** The current detector resolves its model path relative to the working directory, so launching from the project root is recommended.

The current implementation should be treated as an experimental touchless-control prototype rather than a fully reliable replacement for a conventional mouse.

## Future Improvements

- Improve gesture robustness using better geometric features and temporal filtering.
- Add configurable gesture-to-action mappings.
- Implement motion-based scrolling with dead zones and adjustable sensitivity.
- Improve click detection and prevent unintended repeated actions.
- Add automated tests for gesture classification and action mapping.
- Benchmark recognition stability, frame rate, and end-to-end latency.
- Explore a trained machine-learning classifier using hand-landmark features or landmark sequences.
- Improve error handling, configuration, and cross-platform support where practical.

These are potential development directions, not features claimed to be implemented.

## Project Goal

AI Gesture Engine explores how computer vision can make human–computer interaction more natural by turning ordinary hand poses into digital input.

The project serves as a foundation for learning about computer vision, landmark geometry, temporal filtering, real-time processing, and operating-system input control. Its modular design also provides room to experiment with more advanced gesture-recognition techniques and accessible interaction interfaces.

## Author

**KUNSH-bit**
