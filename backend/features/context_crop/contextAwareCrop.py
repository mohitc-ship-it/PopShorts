from face_tracker import FaceTracker
from speaker_detector import SpeakerDetector
from cropper import Cropper
from smoother import SmoothCamera
import cv2

# VIDEO_PATH = "input.mp4"
VIDEO_PATH = "/Users/consultadd/Desktop/Hackathon/PopShorts/testing/testing-assets/test_videos/test2_trimmed.mp4"
OUTPUT_PATH = "/Users/consultadd/Desktop/Hackathon/PopShorts/testing/testing-assets/test_videos/output_portrait.mp4"

face_tracker = FaceTracker()
speaker_detector = SpeakerDetector(VIDEO_PATH)
cropper = Cropper()
camera = SmoothCamera()

cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (1080, 1920)
)

frame_idx = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    time_sec = frame_idx / fps

    faces = face_tracker.detect_and_track(frame)
    active_speaker_id = speaker_detector.get_stable_speaker(time_sec, faces)

    if active_speaker_id is not None:
        target_crop = cropper.get_crop(frame, faces, active_speaker_id)
        smooth_crop = camera.smooth(target_crop)
        portrait_frame = cropper.apply_crop(frame, smooth_crop)
    else:
        # No speaker detected, crop based on largest face
        target_crop = cropper.get_default_crop(frame, faces)
        smooth_crop = camera.smooth(target_crop)
        portrait_frame = cropper.apply_crop(frame, smooth_crop)

    out.write(portrait_frame)
    frame_idx += 1

cap.release()
out.release()
print("✅ Context-aware portrait video generated")
