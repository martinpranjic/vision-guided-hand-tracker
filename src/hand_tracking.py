import time


import cv2
import mediapipe as mp

options = mp.tasks.vision.HandLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=1,
)

hand_landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Could not open camera.")

while True:
    success, frame = camera.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame,
    )

    timestamp_ms = int(time.monotonic() * 1000)

    result = hand_landmarker.detect_for_video(
        mp_image,
        timestamp_ms,
    )

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]
        index_finger_tip = hand[8]

        frame_height, frame_width, _ = frame.shape

        x = int(index_finger_tip.x * frame_width)
        y = int(index_finger_tip.y * frame_height)

        cv2.circle(frame, (x, y), 12, (0, 255, 0), -1)

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

camera.release()
hand_landmarker.close()
cv2.destroyAllWindows()
