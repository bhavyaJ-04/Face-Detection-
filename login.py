import cv2
import face_recognition
import numpy as np
from firebase_admin import db

def login_voter(voter_id, image_path):
    # Retrieve the voter data from Firebase
    ref = db.reference(f'Voters/{voter_id}')
    voter_data = ref.get()

    if not voter_data:
        print("Voter ID not found.")
        return False

    img = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    try:
        # Calculate face encoding for the login attempt
        login_encoding = face_recognition.face_encodings(rgb_image)[0]
        stored_encoding = np.array(voter_data['face_encoding'])

        # Compare encodings
        matches = face_recognition.compare_faces([stored_encoding], login_encoding)
        return matches[0]
    except IndexError:
        print("No face detected. Please try again with a clear image.")
        return False
