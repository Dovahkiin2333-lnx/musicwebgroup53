function loadUploadSection() {
    fetch('/user/profile/sections/upload-music')
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            setupFormSubmission();
        });
}

function setupFormSubmission() {
    const form = document.getElementById('uploadMusicForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const statusDiv = document.getElementById('uploadStatus');

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = data.message;
            statusDiv.style.color = data.success ? 'green' : 'red';
            if (data.success) form.reset();
        })
        .catch(error => {
            statusDiv.textContent = "Upload failed: " + error;
            statusDiv.style.color = 'red';
        });
    });
}

document.querySelector('[data-section="upload"]').addEventListener('click', loadUploadSection);
