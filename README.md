🧠 EyeVox – Gaze & Voice Controlled Interaction System
EyeVox is a biometric authentication and interaction system that allows users to control their desktop using gaze direction and voice commands. It combines computer vision and speech recognition to enable hands-free navigation and secure login.

## 🎥 Demo Video

👉 [Watch EyeVox in Action (3-min Demo)](https://drive.google.com/file/d/1WAhIng_wFkA21rsPhMhSmac_QG18lU6l/view?usp=drive_link)

🚀 Features
🎯 Gaze-based cursor control using iris tracking

🗣️ Voice command execution (e.g., move, click, open)

🔐 Biometric authentication via gaze + voice phrase

🧑‍💻 GUI for registration and login (Tkinter-based)

🛡️ Visual feedback and security log tracking

🧩 Built with OpenCV, MediaPipe, and SpeechRecognition

📦 Project Structure
graphql
Copy
Edit
EyeVox/
│
├── credentials/               # Stores enrolled user data (gaze + voice)
├── main_gui.py                # Main GUI script (login/signup interface)
├── enroll_user.py             # Script for user registration
├── authenticate_user.py       # Script for user authentication
├── voice_commands.py          # Handles real-time voice commands
├── gaze_controller.py         # Controls mouse using eye tracking
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
⚙️ Installation
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/Ayushfulsundar08/EyeVox.git
cd EyeVox
2. Create and Activate a Virtual Environment (Optional but Recommended)
bash
Copy
Edit
python -m venv venv
source venv/bin/activate      # On Linux/macOS
venv\Scripts\activate         # On Windows
3. Install Required Libraries
bash
Copy
Edit
pip install -r requirements.txt
If you get camera or mic-related errors, ensure permissions are enabled on your OS.

🧪 How to Use
🔑 Sign Up
Run main_gui.py

Click Sign Up

Look left (or predefined direction) and say "EyeVox"

Your gaze and voice will be saved as credentials

🔐 Login
Run main_gui.py

Click Login

Look in the same direction and say "EyeVox"

If matched, access will be granted

🎮 Control Mode
Once authenticated:

Use gaze direction to move the cursor

Use voice commands (e.g., "click", "type", "open browser")

📸 Screenshots (Optional)
Add a folder screenshots/ and update this section with images or gifs.

🧱 Requirements
Python 3.8+

OpenCV

MediaPipe

pyttsx3

speechrecognition

pyautogui

tkinter

numpy

sounddevice

scipy

👨‍💻 Developer
Ayush Fulsundar
B.Tech Cyber Security @ MIT ADT University
🔗 GitHub

📄 License
This project is for educational and research purposes. Feel free to fork or contribute.

