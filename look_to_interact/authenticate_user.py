import os
import sys
import numpy as np
import wavio
import cv2
import mediapipe as mp
import time
import subprocess
import sounddevice as sd
from scipy.io.wavfile import read as read_wav
from scipy.spatial.distance import cosine
import glob

# 📁 Path resolution (for .py or .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
GAZE_VECTOR_FILE = os.path.join(CREDENTIALS_DIR, "gaze_vector.txt")
VOICE_SAMPLE_GLOB = os.path.join(CREDENTIALS_DIR, "voice_sample_*.wav")
VOICE_INPUT_FILE = os.path.join(CREDENTIALS_DIR, "voice_input.wav")

def initialize_credentials():
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)
        print("📁 'credentials' folder created.")

    if not os.path.exists(GAZE_VECTOR_FILE):
        with open(GAZE_VECTOR_FILE, "w") as f:
            f.write("0.5 " * 4)  # dummy gaze vector
        print("👁️ Dummy gaze vector created.")

    if not glob.glob(VOICE_SAMPLE_GLOB):
        dummy_audio = np.zeros((44100 * 3, 1), dtype='int16')
        wavio.write(os.path.join(CREDENTIALS_DIR, "voice_sample_1.wav"), dummy_audio, 44100, sampwidth=2)
        print("🎙️ Dummy voice sample created.")

initialize_credentials()

def extract_gaze_vector_from_frame(frame):
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_eye_indices = [468, 469, 470, 471, 472]
            right_eye_indices = [473, 474, 475, 476, 477]

            left_iris = np.mean([[landmarks[i].x, landmarks[i].y] for i in left_eye_indices], axis=0)
            right_iris = np.mean([[landmarks[i].x, landmarks[i].y] for i in right_eye_indices], axis=0)

            gaze_vector = np.concatenate((left_iris, right_iris))
            return gaze_vector
    return None

def record_voice(output_file, duration=3, samplerate=44100):
    print("🎙️ Recording voice now. Please say your phrase...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wavio.write(output_file, recording, samplerate, sampwidth=2)
    print("✅ Voice recorded.")

def compare_gaze_vectors(vector1, vector2):
    if vector1 is None or vector2 is None:
        return 0
    similarity = 1 - cosine(vector1, vector2)
    return similarity

def compare_voice(reference_path, input_path):
    try:
        sr1, ref_data = read_wav(reference_path)
        sr2, input_data = read_wav(input_path)

        min_len = min(len(ref_data), len(input_data))
        ref_data = ref_data[:min_len]
        input_data = input_data[:min_len]

        similarity = 1 - cosine(ref_data.flatten(), input_data.flatten())
        return similarity
    except Exception as e:
        print(f"❌ Error comparing voice: {e}")
        return 0

def authenticate():
    print("🔐 Starting authentication...")
    print("🧿 Please look in the same direction as during enrollment...")

    cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture frame.")
        return False, 0, 0

    current_gaze_vector = extract_gaze_vector_from_frame(frame)
    if current_gaze_vector is None:
        print("❌ Failed to extract gaze vector.")
        return False, 0, 0

    with open(GAZE_VECTOR_FILE, "r") as f:
        registered_gaze = np.array(list(map(float, f.read().strip().split())))

    gaze_similarity = compare_gaze_vectors(registered_gaze, current_gaze_vector)
    print(f"🧠 Gaze similarity: {gaze_similarity:.2f}")

    if gaze_similarity < 0.85:
        print("❌ Gaze does not match. Access denied.")
        return False, gaze_similarity, 0

    record_voice(VOICE_INPUT_FILE)

    # ➕ Match against multiple samples
    voice_samples = glob.glob(VOICE_SAMPLE_GLOB)
    voice_match_found = False
    best_voice_similarity = 0

    for sample in voice_samples:
        similarity = compare_voice(sample, VOICE_INPUT_FILE)
        print(f"🔎 Compared with {os.path.basename(sample)} → similarity: {similarity:.2f}")
        if similarity > best_voice_similarity:
            best_voice_similarity = similarity
        if similarity >= 0.85:
            voice_match_found = True
            break

    if voice_match_found:
        print("✅ Authentication successful! Access granted.")
        print("🚀 Launching EyeVox...")
        try:
            subprocess.Popen(["python", "voice_commands.py"])
        except Exception as e:
            print(f"❌ Failed to launch EyeVox: {e}")
        return True, gaze_similarity, best_voice_similarity
    else:
        print("❌ Voice does not match any sample. Access denied.")
        return False, gaze_similarity, best_voice_similarity

if __name__ == "__main__":
    authenticate()
