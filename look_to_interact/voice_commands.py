import os
import pickle
import time
import cv2
import subprocess
import pyautogui
import threading
import speech_recognition as sr
import mediapipe as mp
import webbrowser

# Define the base directory and credentials directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_DIR = os.path.join(BASE_DIR, "auth_data")
FACE_ENCODINGS_FILE = os.path.join(AUTH_DIR, "face_encodings.pkl")
VOICE_PASSPHRASE_FILE = os.path.join(AUTH_DIR, "voice_passphrase.txt")

# Create the credentials directory if it doesn't exist
os.makedirs(AUTH_DIR, exist_ok=True)

# Initialize MediaPipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Get screen size for cursor movement
screen_width, screen_height = pyautogui.size()

class VoiceGazeController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.running = True
        self.voice_thread = threading.Thread(target=self.listen_commands, daemon=True)
        self.voice_thread.start()

    def listen_commands(self):
        with sr.Microphone() as source:
            print("🎤 Voice input ready...")
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")
                    self.process_command(command)
                    time.sleep(1)  # Delay to avoid over-processing
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"🤷 Couldn't understand, please try again.")

    def process_command(self, command):
        if command.startswith("open "):
            app = command[5:]
            self.open_application(app)
        elif command.startswith("type "):
            text = command[5:]
            self.type_text(text)
        elif command == "click":
            pyautogui.click()
            print("🖱️ Clicked!")
        elif command == "double click":
            pyautogui.doubleClick()
            print("🖱️ Double Clicked!")
        elif command == "scroll up":
            pyautogui.scroll(500)
            print("⬆️ Scrolled Up!")
        elif command == "scroll down":
            pyautogui.scroll(-500)
            print("⬇️ Scrolled Down!")
        elif command == "exit":
            print("👋 Exiting EyeVox...")
            self.running = False

    def open_application(self, app):
        try:
            if app == "notepad":
                subprocess.Popen("notepad.exe")
            elif app == "chrome":
                subprocess.Popen("chrome.exe")
            elif app == "youtube":
                webbrowser.open("https://www.youtube.com")
            else:
                webbrowser.open(f"https://www.google.com/search?q={app}")
        except Exception as e:
            print(f"Error launching app: {e}")

    def type_text(self, text):
        pyautogui.typewrite(text)

    def run_gaze_control(self):
        cap = cv2.VideoCapture(0)
        print("🧿 Gaze control active. Press 'q' to quit.")

        while self.running:
            success, frame = cap.read()
            if not success:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                left_iris = landmarks[474]
                right_iris = landmarks[469]

                left_x, left_y = int(left_iris.x * frame.shape[1]), int(left_iris.y * frame.shape[0])
                right_x, right_y = int(right_iris.x * frame.shape[1]), int(right_iris.y * frame.shape[0])

                # Draw rectangles around both irises
                box_size = 30
                cv2.rectangle(frame, (left_x - box_size, left_y - box_size),
                              (left_x + box_size, left_y + box_size), (0, 255, 0), 2)
                cv2.rectangle(frame, (right_x - box_size, right_y - box_size),
                              (right_x + box_size, right_y + box_size), (0, 255, 0), 2)

                avg_x = (left_x + right_x) // 2
                avg_y = (left_y + right_y) // 2

                screen_x = screen_width * (avg_x / frame.shape[1])
                screen_y = screen_height * (avg_y / frame.shape[0])

                pyautogui.moveTo(screen_x, screen_y, duration=0.1)  # smooth movement

            cv2.imshow("EyeVox", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        cap.release()
        cv2.destroyAllWindows()
        print("🛑 Gaze control stopped.")

def record_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Say your passphrase clearly...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            return audio
        except sr.WaitTimeoutError:
            return None

def authenticate_user():
    print("\n🔐 Starting Authentication...")

    if not os.path.exists(FACE_ENCODINGS_FILE):
        print("❌ Face data not found!")
        return False

    cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture image.")
        return False

    import face_recognition
    known_enc = pickle.load(open(FACE_ENCODINGS_FILE, "rb"))
    unknown_encs = face_recognition.face_encodings(frame)

    if not unknown_encs:
        print("❌ No face detected.")
        return False

    if not face_recognition.compare_faces([known_enc], unknown_encs[0])[0]:
        print("🚫 Face authentication failed.")
        return False

    print("✅ Face verified!")

    if not os.path.exists(VOICE_PASSPHRASE_FILE):
        print("❌ Voice passphrase not found!")
        return False

    audio = record_voice()
    if not audio:
        return False

    spoken_pass = extract_voice_features(audio)
    with open(VOICE_PASSPHRASE_FILE, "r") as f:
        stored_pass = f.read().strip()

    if spoken_pass and spoken_pass.lower() == stored_pass.lower():
        print("✅ Voice verified! Access granted.")
        return True
    else:
        print("🚫 Voice authentication failed.")
        return False

def extract_voice_features(audio):
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio)
    except:
        return None

import sys

if __name__ == "__main__":
    print("🚀 Starting EyeVox controller...")
    controller = VoiceGazeController()
    controller.run_gaze_control()
