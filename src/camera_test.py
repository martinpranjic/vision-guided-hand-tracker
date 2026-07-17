import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Could not open camera.")

success, frame = camera.read()
camera.release()

if not success:
    raise RuntimeError("Could not capture a frame.")

print(frame.shape)