import os
import numpy as np
import cv2
import mediapipe as mp
import time
import wavio
import sounddevice as sd

CREDENTIALS_DIR = "credentials"
GAZE_VECTOR_FILE = os.path.join(CREDENTIALS_DIR, "gaze_vector.txt")
VOICE_REFERENCE_FILE = os.path.join(CREDENTIALS_DIR, "voice_reference.wav")

os.makedirs(CREDENTIALS_DIR, exist_ok=True)

# 🎯 Gaze extractor with visual camera feed
def extract_gaze_with_preview():
    cap = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, refine_landmarks=True)

    gaze_vector = None
    start_time = time.time()
    print("🧿 Look straight. Capturing gaze vector...")

    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw facial landmarks
                for i in [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]:
                    pt = face_landmarks.landmark[i]
                    x, y = int(pt.x * frame.shape[1]), int(pt.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                left_eye = np.mean([[face_landmarks.landmark[i].x, face_landmarks.landmark[i].y] for i in range(468, 473)], axis=0)
                right_eye = np.mean([[face_landmarks.landmark[i].x, face_landmarks.landmark[i].y] for i in range(473, 478)], axis=0)
                gaze_vector = np.concatenate((left_eye, right_eye))

        cv2.putText(frame, "Look straight - capturing gaze", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Gaze Enrollment", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return gaze_vector

# 🎤 Voice recorder with countdown animation
def record_voice_with_animation(output_file, duration=3, samplerate=44100):
    width, height = 500, 120
    win_name = "🎙️ Voice Recorder"
    cv2.namedWindow(win_name)

    for i in range(3, 0, -1):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, f"Recording in {i}...", (100, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4)
        cv2.imshow(win_name, frame)
        cv2.waitKey(1000)

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, "Recording...", (130, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
    cv2.imshow(win_name, frame)
    cv2.waitKey(500)

    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wavio.write(output_file, recording, samplerate, sampwidth=2)

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, "✅ Voice saved!", (130, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
    cv2.imshow(win_name, frame)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

# 📝 Save gaze and voice credentials
def enroll_user():
    gaze = extract_gaze_with_preview()
    if gaze is not None:
        with open(GAZE_VECTOR_FILE, "w") as f:
            f.write(" ".join(map(str, gaze)))
        print("✅ Gaze vector saved.")
    else:
        print("❌ Failed to capture gaze vector.")

    print("🎤 Get ready to speak your authentication phrase...")
    record_voice_with_animation(VOICE_REFERENCE_FILE)
    print("✅ Enrollment complete.")

if __name__ == "__main__":
    enroll_user()
