import cv2
from helpers.gaze_tracking import GazeTracker, GazeDirection

gt = GazeTracker()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()

    if not success:
        continue

    gt.update(frame)

    annotated_frame = gt.get_last_annotated_frame()
    direction = gt.get_gaze_direction()

    cv2.flip(annotated_frame, 1)
    cv2.putText(annotated_frame, f'{direction.name}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow('Robot Gaze', annotated_frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break