# AI Gesture Engine
It is a Python-based computer vision project that transforms ordinary webcam input into recognizable hand gestures in real time. It combines MediaPipe's pretrained hand-landmark detection model with a custom rule-based classification engine to interpret hand poses without requiring dedicated sensors, wearable hardware, or a cloud-based inference service.

The project explores a foundation for more natural, accessible, and intuitive interaction between humans and computers.

**Current status:** Working prototype — real-time hand detection and basic gesture classification.

---

## Overview

Traditional computer interaction relies heavily on physical input devices such as keyboards, mice, and touchscreens. AI Gesture Engine explores an alternative: using natural hand movements as an input interface.

A standard webcam captures the user's hand, a computer vision model identifies its landmarks, and a custom classifier interprets the resulting coordinate patterns into gesture labels.

The system is designed with a modular architecture, making it easier to extend the recognition engine and eventually connect gestures to desktop actions, productivity tools, and other interactive applications.

## Key Features

- **Real-Time Hand Tracking:** Detects and tracks hand landmarks from a live webcam feed.
- **21-Point Landmark Representation:** Processes the wrist, finger joints, and fingertips to represent hand geometry.
- **Coordinate-Based Classification:** Uses geometric rules to distinguish supported hand poses.
- **Wrist-Relative Coordinates:** Transforms landmark positions relative to the wrist to reduce dependence on where the hand appears in the frame.
- **Live Visual Feedback:** Displays the detected hand skeleton, gesture label, and debugging information.
- **Local Processing:** Runs detection and classification locally without requiring cloud inference.
- **Modular Architecture:** Separates video processing, landmark detection, and gesture classification into independent components.

## Supported Gestures

| Gesture | Classification |
|---|---|
| Open Palm | All five fingers detected as extended |
| Peace Sign | Index and middle fingers detected as extended |
| Thumbs Up | Thumb-extension pattern with an additional vertical-position check |
| Fist | All five fingers detected as folded |
| Rock Sign | Index and little fingers detected as extended |
| Pointing Up | Index finger detected as extended and pointing upward|
| Pointing Down | Index finger detected as extended and pointing downward|
| Unknown | Hand pose does not match a supported rule |
| No Hand Detected | No hand landmarks returned by the detector |

Recognition is currently based on geometric heuristics rather than a separately trained gesture-classification model. Performance can vary with hand orientation, camera angle, lighting, and individual hand movements.

## System Architecture

The engine follows a modular processing pipeline:

```text
             Webcam Input
                  |
                  v
        OpenCV Frame Capture
                  |
                  v
       MediaPipe Hand Landmarker
                  |
                  v
        21 Hand Landmark Points
                  |
                  v
       NumPy Coordinate Processing
          (Wrist-Relative Data)
                  |
                  v
        Gesture Classification
          (Geometric Rules)
                  |
                  v
       Live Gesture Visualization
```

### Core Modules

**`main.py` — Application Controller**

Manages the webcam stream, coordinates the detector and classifier, displays the recognized gesture and frame-rate information, and handles application shutdown.

**`detector.py` — Computer Vision Layer**

Uses MediaPipe's Hand Landmarker Tasks API to detect hand landmarks in video frames. It converts the detected points into a NumPy array, calculates wrist-relative coordinates, and draws the hand skeleton on the camera feed.

**`gestures.py` — Gesture Recognition Layer**

Evaluates the processed landmark coordinates using geometric conditions. It determines which supported gesture best matches the observed finger configuration and returns the corresponding label with debugging information.

This separation allows the detection pipeline to evolve independently from the gesture-recognition logic.

## Technical Implementation

### 1. Hand Landmark Detection

The MediaPipe Hand Landmarker model estimates 21 three-dimensional landmark coordinates for a detected hand. These points represent important anatomical locations, including the wrist, finger joints, and fingertips.

### 2. Wrist-Relative Coordinate Processing

Rather than relying only on positions within the camera image, the engine subtracts the wrist coordinates from the other landmark coordinates.

For landmark \(i\), the transformation is:

\[
P_i' = P_i - P_{\text{wrist}}
\]

This places the wrist at the coordinate origin and expresses the remaining points relative to it. It reduces sensitivity to the hand's absolute position in the image, although hand scale and orientation can still affect the resulting coordinates.

### 3. Geometric Gesture Classification

The classifier evaluates finger-extension patterns using landmark relationships. For example, it compares fingertip and joint positions to estimate whether individual fingers are extended.

These binary finger states are then matched against predefined patterns to produce a gesture label.

This approach is lightweight, interpretable, and useful for experimentation. It also provides a foundation for exploring more advanced approaches such as temporal filtering, normalized geometric features, and trained gesture classifiers.

### 4. Real-Time Visualization

OpenCV overlays the hand skeleton, detected gesture, debugging information, and frame-rate indicator onto the live camera feed, allowing the recognition pipeline to be observed while it runs.

## Technology Stack

| Technology | Role |
|---|---|
| Python | Core application and recognition logic |
| OpenCV | Webcam capture, image processing, and visualization |
| MediaPipe Tasks | Pretrained hand-landmark detection |
| NumPy | Landmark arrays and coordinate transformations |


## Current Limitations

The project is an evolving prototype, and several areas remain open for improvement:

- **Gesture stability:** Individual frames are classified independently, so labels can fluctuate during movement.
- **Orientation sensitivity:** Some geometric rules, particularly thumb detection, can behave differently depending on hand orientation and camera mirroring.
- **Scale sensitivity:** Wrist-relative coordinates are not yet normalized for hand size.
- **Limited gesture vocabulary:** Only a small set of predefined poses is currently supported.
- **No custom-trained classifier:** Gesture recognition currently relies on manually defined geometric rules rather than a model trained on a gesture dataset.

These limitations define concrete engineering opportunities for the next development stages.

## Roadmap

The following are planned improvements, not claims about features already implemented.

- [ ] Expand the gesture vocabulary and improve classification reliability.
- [ ] Introduce configurable gesture-to-action mappings.
- [ ] Evaluate recognition reliability, false activations, frame rate, and end-to-end latency.
- [ ] Explore a trained machine-learning classifier using landmark sequences.

## Project Vision

AI Gesture Engine aims to evolve from a real-time hand-pose recognizer into a flexible gesture-driven interaction layer.

The broader goal is to investigate how computer vision can make digital interfaces more natural and accessible, while keeping the processing pipeline modular, responsive, and locally executable.

The current prototype establishes the core loop: **camera input → hand landmarks → geometric interpretation → real-time feedback.** Future iterations will build on that foundation to explore stable gesture recognition and practical touchless computer interaction.

## Author

**KUNSH-bit**
