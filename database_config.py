import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    """
    Initialize Firebase app with the service account key and Realtime Database URL.
    """
    # Path to your Firebase service account key JSON file
    service_account_path = "serviceAccountKey.json"  # Ensure this file exists in your project directory

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://face-detection-4e986-default-rtdb.asia-southeast1.firebasedatabase.app/"  # Replace with your Firebase Realtime Database URL
        })

def get_database_reference():
    """
    Get the reference to the Firebase Realtime Database root.
    """
    # Initialize Firebase if not already initialized
    initialize_firebase()
    
    # Return database reference
    return db.reference()