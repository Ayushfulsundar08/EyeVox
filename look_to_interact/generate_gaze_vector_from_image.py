import cv2
import mediapipe as mp
import numpy as np
import os

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

# Load the image from credentials folder
img = cv2.imread("credentials/gaze_reference.jpg")
if img is None:
    print("Failed to load image. Make sure 'credentials/gaze_reference.jpg' exists.")
    exit()

rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
results = face_mesh.process(rgb_img)

if not results.multi_face_landmarks:
    print("No face detected in the reference image.")
    exit()

# Extract iris and eye landmarks (left and right)
landmarks = results.multi_face_landmarks[0].landmark
image_height, image_width = img.shape[:2]

def get_iris_center(landmark_indices):
    coords = np.array([
        [landmarks[i].x * image_width, landmarks[i].y * image_height]
        for i in landmark_indices
    ])
    return np.mean(coords, axis=0)

# MediaPipe iris indices
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

left_iris_center = get_iris_center(LEFT_IRIS)
right_iris_center = get_iris_center(RIGHT_IRIS)

# Combine left and right iris centers as the "gaze feature"
gaze_vector = np.concatenate((left_iris_center, right_iris_center))

# Create credentials folder if it doesn't exist
os.makedirs("credentials", exist_ok=True)

# Save gaze vector to file
np.savetxt("credentials/gaze_vector.txt", gaze_vector)

print("✅ Gaze vector saved to credentials/gaze_vector.txt")
