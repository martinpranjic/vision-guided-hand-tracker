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

smoothing_factor = 0.2
return_smoothing_factor = 0.05

smoothed_pan = 0.0
smoothed_tilt = 0.0
servo_center = 90
max_pan_offset = 60
max_tilt_offset = 45

# If camera loses sight of hands for => 2 seconds

return_delay = 2.0
last_hand_seen = time.monotonic()

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

    frame_height, frame_width, _ = frame.shape

    center_x = frame_width // 2
    center_y = frame_height // 2

    cv2.drawMarker(
        frame,
        (center_x, center_y),
        (255, 255, 255),
        cv2.MARKER_CROSS,
        30,
        2,
    )

    if result.hand_landmarks:
        last_hand_seen = time.monotonic()
        hand = result.hand_landmarks[0]
        index_finger_tip = hand[8]

        palm_x = (
            hand[0].x
            + hand[5].x
            + hand[9].x
            + hand[13].x
            + hand[17].x
        ) / 5

        palm_y = (
            hand[0].y
            + hand[5].y
            + hand[9].y
            + hand[13].y
            + hand[17].y
        ) / 5

        x = int(palm_x * frame_width)
        y = int(palm_y * frame_height)

        error_x = x - center_x
        error_y = y - center_y

        pan_command = error_x / center_x
        tilt_command = error_y / center_y

        dead_zone = 0.05

        if abs(pan_command) < dead_zone:
            pan_command = 0.0

        if abs(tilt_command) < dead_zone:
            tilt_command = 0.0

        smoothed_pan = (
            smoothing_factor * pan_command
            + (1 - smoothing_factor) * smoothed_pan
        )

        smoothed_tilt = (
            smoothing_factor * tilt_command
            + (1 - smoothing_factor) * smoothed_tilt
        )

        cv2.line(
            frame,
            (center_x, center_y),
            (x, y),
            (255, 0, 0),
            2,
        )

        cv2.putText(
            frame,
            f"Error x: {error_x}, Error y: {error_y}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        frame_height, frame_width, _ = frame.shape

        cv2.circle(frame, (x, y), 12, (0, 255, 0), -1)

    else:
        seconds_without_hand = time.monotonic() - last_hand_seen

        if seconds_without_hand >= return_delay:
            smoothed_pan = (1 - return_smoothing_factor) * smoothed_pan
            smoothed_tilt = (1 - return_smoothing_factor) * smoothed_tilt

    pan_angle = servo_center + smoothed_pan * max_pan_offset
    tilt_angle = servo_center - smoothed_tilt * max_tilt_offset

    pan_angle = int(round(max(30, min(150, pan_angle))))
    tilt_angle = int(round(max(45, min(135, tilt_angle))))

    cv2.putText(
        frame,
        f"Pan angle: {pan_angle:.2f}, Tilt: {tilt_angle:.2f}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

camera.release()
hand_landmarker.close()
cv2.destroyAllWindows()
