document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('video');

    // Start video feed for face capture (if needed for registration)
    if (video) {
        navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
            video.srcObject = stream;
        }).catch((err) => console.error('Error accessing camera:', err));
    }

    // Registration logic
    window.registerUser = async function () {
        const voterId = document.getElementById('voter-id-register').value;
        const faceImage = document.getElementById('register-face-image').files[0];

        if (!voterId || !faceImage) {
            showAlert('Please provide both Voter ID and face image.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('voter_id', voterId);
        formData.append('face_image', faceImage);

        try {
            const response = await fetch('/register', {
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
            console.error('Error during registration:', error);
            showAlert('An error occurred during registration. Please try again.', 'error');
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
