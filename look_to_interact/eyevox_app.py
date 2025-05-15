import os
import numpy as np
import wavio
import cv2
import mediapipe as mp
import time
import subprocess
from scipy.io.wavfile import read as read_wav
from scipy.spatial.distance import cosine
import sounddevice as sd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ------------------------- File Paths -------------------------
CREDENTIALS_DIR = "credentials"
LOGS_DIR = "logs"
GAZE_VECTOR_FILE = os.path.join(CREDENTIALS_DIR, "gaze_vector.txt")
VOICE_REFERENCE_FILE = os.path.join(CREDENTIALS_DIR, "voice_reference.wav")
VOICE_INPUT_FILE = os.path.join(CREDENTIALS_DIR, "voice_input.wav")

# ------------------------- Initialization -------------------------
def initialize_system():
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    if not os.path.exists(GAZE_VECTOR_FILE):
        with open(GAZE_VECTOR_FILE, "w") as f:
            f.write("0.5 " * 4)

    if not os.path.exists(VOICE_REFERENCE_FILE):
        dummy_audio = np.zeros((44100 * 3, 1), dtype='int16')
        wavio.write(VOICE_REFERENCE_FILE, dummy_audio, 44100, sampwidth=2)

initialize_system()

# ------------------------- Utility Functions -------------------------
def log_event(message):
    with open(os.path.join(LOGS_DIR, "auth_log.txt"), "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] {message}\n")

def check_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False
    ret, _ = cap.read()
    cap.release()
    return ret

def extract_gaze(frame):
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_eye = np.mean([[landmarks[i].x, landmarks[i].y] for i in range(468, 473)], axis=0)
            right_eye = np.mean([[landmarks[i].x, landmarks[i].y] for i in range(473, 478)], axis=0)
            return np.concatenate((left_eye, right_eye))
    return None

def record_voice(output_file, duration=3, samplerate=44100):
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wavio.write(output_file, recording, samplerate, sampwidth=2)

def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        return 0.0
    return 1 - cosine(vec1, vec2)

def compare_voice():
    try:
        sr1, ref = read_wav(VOICE_REFERENCE_FILE)
        sr2, inp = read_wav(VOICE_INPUT_FILE)
        length = min(len(ref), len(inp))
        return cosine_similarity(ref[:length].flatten(), inp[:length].flatten())
    except:
        return 0.0

# ------------------------- Core Logic -------------------------
def authenticate():
    if not check_camera():
        messagebox.showerror("Error", "Cannot access webcam.")
        return False, 0.0, 0.0

    cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False, 0.0, 0.0

    current_gaze = extract_gaze(frame)
    try:
        with open(GAZE_VECTOR_FILE, "r") as f:
            saved_gaze = np.array(list(map(float, f.read().strip().split())))
    except:
        return False, 0.0, 0.0

    gaze_score = cosine_similarity(current_gaze, saved_gaze)
    if gaze_score < 0.85:
        log_event(f"FAILED - Gaze mismatch ({gaze_score:.2f})")
        return False, gaze_score, 0.0

    record_voice(VOICE_INPUT_FILE)
    voice_score = compare_voice()
    if voice_score >= 0.85:
        log_event(f"SUCCESS - Gaze {gaze_score:.2f}, Voice {voice_score:.2f}")
        try:
            subprocess.Popen(["python", "voice_commands.py"])
        except Exception as e:
            log_event(f"ERROR launching voice_commands.py: {e}")
        return True, gaze_score, voice_score
    else:
        log_event(f"FAILED - Voice mismatch ({voice_score:.2f})")
        return False, gaze_score, voice_score

def register_credentials():
    if not check_camera():
        messagebox.showerror("Error", "Cannot access webcam.")
        return False

    cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False

    gaze = extract_gaze(frame)
    if gaze is not None:
        with open(GAZE_VECTOR_FILE, "w") as f:
            f.write(" ".join(map(str, gaze)))
    else:
        return False

    record_voice(VOICE_REFERENCE_FILE)
    log_event("CREDENTIALS REGISTERED")
    return True

# ------------------------- GUI -------------------------
def on_auth():
    success, gaze, voice = authenticate()
    if success:
        messagebox.showinfo("Access Granted", f"✅ Gaze: {gaze:.2f}\n🎤 Voice: {voice:.2f}")
    else:
        messagebox.showerror("Access Denied", f"❌ Gaze: {gaze:.2f}\n🎤 Voice: {voice:.2f}")

def on_register():
    if register_credentials():
        messagebox.showinfo("Success", "✅ Credentials registered.")
    else:
        messagebox.showerror("Failed", "❌ Registration failed.")

app = tk.Tk()
app.title("EyeVox Secure Access")
app.geometry("320x260")
app.configure(bg="black")

label = tk.Label(app, text="👁️ EyeVox", font=("Arial", 24), fg="cyan", bg="black")
label.pack(pady=20)

tk.Button(app, text="Authenticate", command=on_auth, bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)
tk.Button(app, text="Register Credentials", command=on_register, bg="green", fg="white", font=("Arial", 12)).pack(pady=5)

app.mainloop()
