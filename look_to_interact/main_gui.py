import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import authenticate_user as auth_module
import time
import speech_recognition as sr

# ---------------- GUI Functions ----------------
def handle_authenticate():
    status_label.config(text="🔍 Authenticating...", fg="yellow")
    app.update()

    success, gaze_score, voice_score = auth_module.authenticate()

    if success:
        status_label.config(text="✅ Access Granted!", fg="lime")
        messagebox.showinfo("Access Granted", f"Gaze Match: {gaze_score:.2f}\nVoice Match: {voice_score:.2f}")
        time.sleep(1)
        minimize_window()
        threading.Thread(target=run_voice_gaze_control, daemon=True).start()
    else:
        status_label.config(text="❌ Access Denied!", fg="red")
        messagebox.showerror("Access Denied", f"Gaze Match: {gaze_score:.2f}\nVoice Match: {voice_score:.2f}")

def register_credentials():
    status_label.config(text="📝 Registering credentials...", fg="yellow")
    app.update()

    try:
        subprocess.run(["python", "enroll_user.py"], check=True)
        success = True
    except subprocess.CalledProcessError:
        success = False

    if success:
        status_label.config(text="✅ Credentials Registered", fg="lime")
        messagebox.showinfo("Success", "New gaze and voice credentials registered!")
    else:
        status_label.config(text="❌ Registration Failed", fg="red")
        messagebox.showerror("Failed", "Could not register credentials.")

def run_voice_gaze_control():
    try:
        subprocess.run(["python", "voice_commands.py"])
    except Exception as e:
        print(f"⚠️ Error running voice_commands.py: {e}")

def minimize_window():
    app.iconify()

# ---------------- Voice Activation Before Auth ----------------
def listen_for_commands():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"🗣️ Heard: {command}")

                if "sign up" in command:
                    status_label.config(text="🗣️ Heard: Sign up", fg="cyan")
                    app.update()
                    register_button.invoke()

                elif "log in" in command or "login" in command:
                    status_label.config(text="🗣️ Heard: Log in", fg="cyan")
                    app.update()
                    auth_button.invoke()

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print(f"🎤 Voice recognition error: {e}")
            continue

# ---------------- Main Window ----------------
app = tk.Tk()
app.title("EyeVox Access Portal")
app.geometry("380x300")
app.configure(bg="black")

title_label = tk.Label(app, text="👁️ EyeVox", font=("Arial", 28, "bold"), fg="cyan", bg="black")
title_label.pack(pady=20)

auth_button = tk.Button(app, text="🔒 Log In", command=handle_authenticate, bg="#007bff", fg="white", font=("Arial", 14), width=20)
auth_button.pack(pady=10)

register_button = tk.Button(app, text="📝 Sign Up", command=register_credentials, bg="#28a745", fg="white", font=("Arial", 14), width=20)
register_button.pack(pady=5)

exit_button = tk.Button(app, text="❌ Exit", command=app.quit, bg="#dc3545", fg="white", font=("Arial", 14), width=20)
exit_button.pack(pady=10)

status_label = tk.Label(app, text="🎤 Say 'Sign up' or 'Log in'", font=("Arial", 12), fg="white", bg="black")
status_label.pack(pady=10)

# Start voice command listener
threading.Thread(target=listen_for_commands, daemon=True).start()

app.mainloop()
