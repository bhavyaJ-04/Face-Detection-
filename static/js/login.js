document.addEventListener('DOMContentLoaded', function () {
    const captureButton = document.getElementById('capture-button');
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');

    // Start video feed for face capture
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        video.srcObject = stream;
    }).catch((err) => console.error('Error accessing camera:', err));

    // Capture photo
    captureButton.addEventListener('click', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Copy the video frame to the canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Display the captured photo
        canvas.style.display = 'block';
        video.style.display = 'none';

        // Get the captured image data
        const imageData = canvas.toDataURL('image/jpeg');
        console.log('Captured image data:', imageData);
    });

    // Login logic
    window.loginUser = async function () {
        const voterId = document.getElementById('voter-id-login').value;

        if (!voterId) {
            showAlert('Please provide a Voter ID.', 'error');
            return;
        }

        // Get the captured image data from the canvas
        const faceImage = canvas.toDataURL('image/jpeg');

        if (!faceImage) {
            showAlert('Please capture your face before logging in.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('voter_id', voterId);
        formData.append('face_image', faceImage);

        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            if (result.status === 'success') {
                showAlert(result.message, 'success');
            } else {
                showAlert(result.message, 'error');
            }
        } catch (error) {
            console.error('Error during login:', error);
            showAlert('An error occurred during login. Please try again.', 'error');
        }
    };

    // Function to show alert messages
    function showAlert(message, type) {
        const alertSection = document.getElementById('alert-section');
        alertSection.textContent = message;
        alertSection.className = `alert ${type}`;
        alertSection.style.display = 'block';

        setTimeout(() => {
            alertSection.style.display = 'none';
        }, 5000);
    }
});
