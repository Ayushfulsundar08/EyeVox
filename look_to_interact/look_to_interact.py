import os
import pickle
import time
import speech_recognition as sr
import face_recognition
import cv2
import subprocess

# Paths for authentication data
AUTH_DIR = "auth_data"
FACE_ENCODINGS_FILE = os.path.join(AUTH_DIR, "face_encodings.pkl")
VOICE_PASSPHRASE_FILE = os.path.join(AUTH_DIR, "voice_passphrase.txt")

# Ensure auth_data directory exists
os.makedirs(AUTH_DIR, exist_ok=True)

def record_voice():
    """Records a short voice sample and returns the audio data."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Please say your passphrase clearly...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("✅ Voice recorded successfully!")
            return audio
        except sr.WaitTimeoutError:
            print("❌ No voice detected. Try again!")
            return None

def extract_voice_features(audio):
    """Extracts voice features using speech recognition."""
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣 Extracted Text: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Voice not recognized!")
        return None

def authenticate_user():
    """Authenticates a user based on face and voice data."""
    print("\n🟢 Starting Authentication Process...")

    # --- Face Authentication ---
    if not os.path.exists(FACE_ENCODINGS_FILE):
        print("❌ No face data found! Please enroll first.")
        return

    video_capture = cv2.VideoCapture(0)
    print("📷 Capturing face for verification...")
    time.sleep(2)
    ret, frame = video_capture.read()
    video_capture.release()

    if not ret:
        print("❌ Failed to capture face image!")
        return

    known_face_encodings = pickle.load(open(FACE_ENCODINGS_FILE, "rb"))
    unknown_face_encodings = face_recognition.face_encodings(frame)

    if not unknown_face_encodings:
        print("❌ No face detected! Try again.")
        return

    match = face_recognition.compare_faces([known_face_encodings], unknown_face_encodings[0])[0]
    if not match:
        print("🚫 Face authentication failed!")
        return

    print("✅ Face authentication passed!")

    # --- Voice Authentication ---
    if not os.path.exists(VOICE_PASSPHRASE_FILE):
        print("❌ No voice passphrase found! Please enroll first.")
        return

    audio = record_voice()
    if audio is None:
        return

    passphrase = extract_voice_features(audio)
    if not passphrase:
        return

    with open(VOICE_PASSPHRASE_FILE, "r") as f:
        stored_passphrase = f.read().strip()

    if passphrase.lower() == stored_passphrase.lower():
        print("✅ Voice authentication passed! 🎉 Access Granted!")
        
        # 🚀 Start voice and gaze-based interaction system
        print("🚀 Starting EyeVox system...")
        subprocess.Popen(["python", "voice_commands.py"], shell=True)
        print("✅ EyeVox system started successfully!")
    else:
        print("🚫 Voice authentication failed!")

if __name__ == "__main__":
    action = input("Enter 'login' to authenticate: ").strip().lower()

    if action == "login":
        authenticate_user()
    else:
        print("❌ Invalid input! Use 'login'.")
