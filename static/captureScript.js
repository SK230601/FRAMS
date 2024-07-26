// Video and Capture Script
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const imageInput = document.getElementById('image');
const captureForm = document.getElementById('captureForm');

// Get access to the camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        video.srcObject = stream;
        video.play();
    });
}

// Trigger photo capture
captureButton.addEventListener('click', function() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    // Convert canvas data to JPEG
    const dataURL = canvas.toDataURL('image/jpeg', 1.0); // 'image/jpeg' with quality parameter
    imageInput.value = dataURL;
});
