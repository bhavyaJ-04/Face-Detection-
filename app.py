from flask import Flask, render_template, request, jsonify
import os
import cv2
import face_recognition
import numpy as np
import pickle
from firebase_admin import credentials, initialize_app, db
from PIL import Image
import base64
from io import BytesIO

# Flask App Initialization
app = Flask(__name__)

# Firebase Initialization
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {
    "databaseURL": "https://face-detection-4e986-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Directory for Storing Images
ENCODE_FILE = "EncodeFile.p"
if os.path.exists(ENCODE_FILE):
    with open(ENCODE_FILE, 'rb') as file:
        encodeListKnown, voterIds = pickle.load(file)
else:
    encodeListKnown = []
    voterIds = []

# Routes
@app.route("/")
def home():
    return render_template("home.html")  # A landing page with buttons for Login and Registration

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    # Registration Logic
    voter_id = request.form.get("voter_id")
    
    file = request.files.get("face_image")

    if not voter_id or not file:
        return jsonify({"status": "error", "message": "Voter ID and face image are required"}), 400
    
    # Check if the voter ID is already registered
    ref = db.reference(f"Voters/{voter_id}")
    existing_data = ref.get()

    if existing_data:
        return jsonify({"status": "error", "message": "Voter ID already registered"}), 400

    # Save Image Locally
    image_path = os.path.join("Images", f"{voter_id}.jpg")
    file.save(image_path)

    # Encode Face
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_image)

    if len(encodings) > 0:
        for stored_encoding in encodeListKnown:
            matches = face_recognition.compare_faces([stored_encoding], encodings[0], tolerance=0.5)
            if any(matches):
                os.remove(image_path)  # Remove the saved image
                return jsonify({"status": "error", "message": "Face already registered"}), 400


        encodeListKnown.append(encodings[0])
        voterIds.append(voter_id)

        # Update the encodings file
        with open(ENCODE_FILE, 'wb') as file:
            pickle.dump([encodeListKnown, voterIds], file)

        # Save to Firebase
        voter_data = {"voter_id": voter_id, "face_encoding": encodings[0].tolist()}
        db.reference(f"Voters/{voter_id}").set(voter_data)

        return jsonify({"status": "success", "message": "User registered successfully!"})
    else:
        os.remove(image_path)
        return jsonify({"status": "error", "message": "Face not detected. Please try again."}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # Login Logic
    voter_id = request.form.get("voter_id")
    face_image_base64 = request.form.get("face_image")

    if not voter_id or not face_image_base64:
        return jsonify({"status": "error", "message": "Voter ID and face image are required"}), 400

    if voter_id not in voterIds:
        return jsonify({"status": "error", "message": "Voter ID not registered"}), 404

    # Decode Base64 Image
    try:
        face_image_data = base64.b64decode(face_image_base64.split(",")[1])
        face_image = Image.open(BytesIO(face_image_data))
        rgb_image = np.array(face_image)

        # Encode Face
        encodings = face_recognition.face_encodings(rgb_image)
        if len(encodings) == 0:
            return jsonify({"status": "error", "message": "Face not detected"}), 400

        login_encoding = encodings[0]
        stored_encoding = np.array(encodeListKnown[voterIds.index(voter_id)])

        # Compare Encodings
        matches = face_recognition.compare_faces([stored_encoding], login_encoding)
        face_distance = face_recognition.face_distance([stored_encoding], login_encoding)[0]

        if matches[0] and face_distance < 0.5:
            return jsonify({"status": "success", "message": "Login successful!"})
        else:
            return jsonify({"status": "error", "message": "Face does not match voter ID"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error processing image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)



"""
from flask import Flask, render_template, request, jsonify
import os
import cv2
import face_recognition
import numpy as np
import pickle
from firebase_admin import credentials, initialize_app, db
from PIL import Image
import base64
from io import BytesIO

# Flask App Initialization
app = Flask(__name__)

# Firebase Initialization
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {
    "databaseURL": "https://face-detection-4e986-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Directory for Storing Images
#IMAGE_FOLDER = "Images"
#os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Load Encodings
ENCODE_FILE = "EncodeFile.p"
if os.path.exists(ENCODE_FILE):
    with open(ENCODE_FILE, 'rb') as file:
        encodeListKnown, voterIds = pickle.load(file)
else:
    encodeListKnown = []
    voterIds = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    voter_id = request.form.get("voter_id")
    file = request.files.get("face_image")

    if not voter_id or not file:
        return jsonify({"status": "error", "message": "Voter ID and face image are required"}), 400

    # Save Image Locally
    image_path = os.path.join("Images", f"{voter_id}.jpg")
    file.save(image_path)

    # Encode Face
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_image)
    
    if len(encodings) > 0:
        encodeListKnown.append(encodings[0])
        voterIds.append(voter_id)

        # Update the encodings file
        with open(ENCODE_FILE, 'wb') as file:
            pickle.dump([encodeListKnown, voterIds], file)

        # Save to Firebase
        voter_data = {"voter_id": voter_id, "face_encoding": encodings[0].tolist()}
        db.reference(f"Voters/{voter_id}").set(voter_data)

        return jsonify({"status": "success", "message": "User registered successfully!"})
    else:
        os.remove(image_path)
        return jsonify({"status": "error", "message": "Face not detected. Please try again."}), 400


@app.route("/login", methods=["POST"])
def login():
    voter_id = request.form.get("voter_id")
    face_image_base64 = request.form.get("face_image")

    if not voter_id or not face_image_base64:
        return jsonify({"status": "error", "message": "Voter ID and face image are required"}), 400

    if voter_id not in voterIds:
        return jsonify({"status": "error", "message": "Voter ID not registered"}), 404

    # Decode Base64 Image
    try:
        face_image_data = base64.b64decode(face_image_base64.split(",")[1])
        face_image = Image.open(BytesIO(face_image_data))
        rgb_image = np.array(face_image)

        # Encode Face
        encodings = face_recognition.face_encodings(rgb_image)
        if len(encodings) == 0:
            return jsonify({"status": "error", "message": "Face not detected"}), 400

        login_encoding = encodings[0]
        stored_encoding = np.array(encodeListKnown[voterIds.index(voter_id)])

        # Compare Encodings
        matches = face_recognition.compare_faces([stored_encoding], login_encoding)
        face_distance = face_recognition.face_distance([stored_encoding], login_encoding)[0]

        if matches[0] and face_distance < 0.5:  # Adjust threshold as needed
            return jsonify({"status": "success", "message": "Login successful!"})
        else:
            return jsonify({"status": "error", "message": "Face does not match voter ID"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error processing image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)   
"""

"""
    if len(encodings) > 0:
        face_encoding = encodings[0].tolist()
        voter_data = {
            "voter_id": voter_id,
            "face_encoding": face_encoding
        }

        # Save to Firebase
        db.reference(f"Voters/{voter_id}").set(voter_data)
        return jsonify({"status": "success", "message": "User registered successfully!"})
    else:
        os.remove(image_path)
        return jsonify({"status": "error", "message": "Face not detected. Please try again."}), 400


@app.route("/login", methods=["POST"])
def login():
    voter_id = request.form.get("voter_id")
    face_image_base64 = request.form.get("face_image")

    if not voter_id or not face_image_base64:
        return jsonify({"status": "error", "message": "Voter ID and face image are required"}), 400

    # Retrieve Stored Data from Firebase
    voter_ref = db.reference(f"Voters/{voter_id}")
    voter_data = voter_ref.get()

    if not voter_data:
        return jsonify({"status": "error", "message": "Voter ID not registered"}), 404

    # Decode Base64 Image
    face_image_data = base64.b64decode(face_image_base64.split(",")[1])
    face_image = Image.open(BytesIO(face_image_data))
    rgb_image = np.array(face_image)

    # Encode Face
    encodings = face_recognition.face_encodings(rgb_image)
    if len(encodings) == 0:
        return jsonify({"status": "error", "message": "Face not detected"}), 400

    login_encoding = encodings[0]
    stored_encoding = np.array(voter_data["face_encoding"])

    # Compare Encodings
    matches = face_recognition.compare_faces([stored_encoding], login_encoding)
    face_distance = face_recognition.face_distance([stored_encoding], login_encoding)[0]

    if matches[0] and face_distance < 0.6:  # Threshold for face matching
        return jsonify({"status": "success", "message": "Login successful!"})
    else:
        return jsonify({"status": "error", "message": "Face does not match voter ID"}), 401


if __name__ == "__main__":
    app.run(debug=True)
"""
"""
from flask import Flask, render_template, request, jsonify
import os
import cv2
import face_recognition
import pickle
import numpy
from flask_cors import CORS
import base64
import base64
from io import BytesIO
from PIL import Image


app = Flask(__name__)
CORS(app)

# Directory for storing images
IMAGE_FOLDER = 'Images'
os.makedirs(IMAGE_FOLDER,exist_ok=True)

# File for storing face encodings
ENCODE_FILE = 'EncodeFile.p'
if os.path.exists(ENCODE_FILE):
    with open(ENCODE_FILE,'rb') as file:
        encodeListKnown, userIds = pickle.load(file)
else:
    encodeListKnown = []
    userIds = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    
    voter_id = request.form.get('voter_id')
    file = request.files.get('face_image')

    if not voter_id or not file:
        return jsonify({'status': 'error', 'message': 'Voter ID and face image are required'}), 400

    # Save the face image locally
    image_path = os.path.join(IMAGE_FOLDER, f"{voter_id}.jpg")
    file.save(image_path)

    # Encode the face
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_image)

    if len(encodings) > 0:
        encodeListKnown.append(encodings[0])
        userIds.append(voter_id)

        # Update the encodings file
        
        print("pickle dump start")
        with open(ENCODE_FILE, 'wb') as file:
            pickle.dump([encodeListKnown, userIds], file)
        print("pickle dump end")
            
            
        print("Starting to call register_voter")
        from registration import register_voter
        register_voter(voter_id,image_path)
        print("register_voter executed successfully")
        
        return jsonify({'status': 'success', 'message': 'User registered successfully!'})
    else:
        os.remove(image_path)  # Remove the invalid image
        return jsonify({'status': 'error', 'message': 'Face not detected. Please try again.'}), 400
        
        


@app.route('/login', methods=['POST'])
def login():
    voter_id = request.form.get('voter_id')
    face_image_base64 = request.form.get('face_image')

    if not voter_id or not face_image_base64:
        return jsonify({'status': 'error', 'message': 'Voter ID and face image are required'}), 400

    if voter_id not in userIds:
        return jsonify({'status': 'error', 'message': 'Voter ID not registered'}), 400

    # Decode the Base64 image string
    try:
        face_image_data = base64.b64decode(face_image_base64.split(",")[1])
        face_image = Image.open(BytesIO(face_image_data))
        rgb_image = face_image.convert("RGB")
        encodings = face_recognition.face_encodings(numpy.array(rgb_image))

        if len(encodings) > 0:
            face_distances = face_recognition.face_distance(encodeListKnown, encodings[0])
            best_match_index = numpy.argmin(face_distances)

            if face_distances[best_match_index] <= 0.6:  # Threshold
                if userIds[best_match_index] == voter_id:
                    return jsonify({'status': 'success', 'message': 'Login successful!'})
                else:
                    return jsonify({'status': 'error', 'message': 'Face does not match voter ID'}), 401
            else:
                return jsonify({'status': 'error', 'message': 'Face not recognized'}), 401
        else:
            return jsonify({'status': 'error', 'message': 'Face not detected'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing image: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
"""