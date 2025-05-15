import cv2
import dlib
import pyautogui
import speech_recognition as sr
import subprocess
import webbrowser
import threading
import numpy as np
import time

# Load the pre-trained shape predictor model
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

# Load face detector
detector = dlib.get_frontal_face_detector()

# Get the screen dimensions
screen_width, screen_height = pyautogui.size()

# Initialize the camera
cap = cv2.VideoCapture(0)

class VoiceGazeController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.running = True
        self.blink_count = 0
        self.blink_threshold = 2  # Number of blinks required to trigger a click
        self.start_voice_thread()

    def start_voice_thread(self):
        # Start a separate thread for voice commands
        threading.Thread(target=self.listen_commands, daemon=True).start()

    def listen_commands(self):
        with sr.Microphone() as source:
            print("Voice input ready. Speak to open applications or type...")
            while self.running:
                try:
                    audio = self.recognizer.listen(source)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")
                    self.process_command(command)
                except sr.UnknownValueError:
                    print("Sorry, I didn't catch that.")
                except sr.RequestError:
                    print("Error with the speech recognition service.")
                except Exception as e:
                    print(f"Error during voice recognition: {e}")

    def process_command(self, command):
        if command.startswith("open "):
            app_name = command[5:]
            self.open_application(app_name)
        elif command.startswith("type "):
            text_to_type = command[5:]
            self.type_text(text_to_type)
        elif command == "exit":
            print("Exiting...")
            self.running = False

    def open_application(self, app_name):
        try:
            if app_name.lower() in ["notepad", "notepad++"]:
                subprocess.Popen("notepad.exe")
            elif app_name.lower() == "youtube":
                webbrowser.open("https://www.youtube.com")
            elif app_name.lower() == "chrome":
                subprocess.Popen("chrome.exe")
            else:
                print(f"Sorry, I couldn't find {app_name}")
        except Exception as e:
            print(f"Error opening application: {e}")

    def type_text(self, text):
        pyautogui.typewrite(text)
        print(f"Typing: {text}")

    def run_gaze_control(self):
        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("Error: Camera feed not available.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)
                
                left_eye_top = landmarks.part(37).y
                left_eye_bottom = landmarks.part(41).y
                right_eye_top = landmarks.part(44).y
                right_eye_bottom = landmarks.part(38).y
                
                left_ear_denominator = landmarks.part(39).x - landmarks.part(36).x
                right_ear_denominator = landmarks.part(45).x - landmarks.part(42).x
                
                if left_ear_denominator != 0 and right_ear_denominator != 0:
                    left_eye_aspect_ratio = (left_eye_bottom - left_eye_top) / left_ear_denominator
                    right_eye_aspect_ratio = (right_eye_bottom - right_eye_top) / right_ear_denominator

                    if left_eye_aspect_ratio < 0.25 and right_eye_aspect_ratio < 0.25:
                        self.blink_count += 1
                        time.sleep(0.3)
                    else:
                        if self.blink_count >= self.blink_threshold:
                            pyautogui.click()
                            print("Mouse clicked!")
                        self.blink_count = 0
                    
                    eye_center_x = (landmarks.part(36).x + landmarks.part(45).x) // 2
                    eye_center_y = (landmarks.part(37).y + landmarks.part(44).y) // 2
                    cursor_x = min(max(eye_center_x / frame.shape[1], 0), 1) * screen_width
                    cursor_y = min(max(eye_center_y / frame.shape[0], 0), 1) * screen_height
                    pyautogui.moveTo(cursor_x, cursor_y)

            cv2.imshow('Gaze Control', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = VoiceGazeController()
    controller.run_gaze_control()
