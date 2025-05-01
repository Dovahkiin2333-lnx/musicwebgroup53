function loadUploadSection() {
    fetch('/user/profile/sections/my-collection')
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            setupFormSubmission();
        });
}

document.querySelector('[data-section="collection"]').addEventListener('click', loadUploadSection);