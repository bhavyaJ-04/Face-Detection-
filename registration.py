import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, db
from database_config import initialize_firebase, get_database_reference


#initialize_firebase()

def register_voter(voter_id, image_path):
    print("register_voter initialized")
    img = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    try:
        # Calculate face encoding
        face_encoding = face_recognition.face_encodings(rgb_image)[0]
        encoding_list = face_encoding.tolist()

        ref = db.reference('Voters')
        voter_data = {
            "voter_id": voter_id,
            "face_encoding": encoding_list,
        }
        ref.child(voter_id).set(voter_data)
        print("Voter registered successfully!")
    except IndexError:
        print("No face detected. Please try again with a clear image.")
