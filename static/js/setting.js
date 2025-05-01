function loadUploadSection() {
    fetch('/user/profile/sections/setting')
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            setupFormSubmission();
        });
}

function submitForm(formType) {
    const form= document.getElementById(formType + 'Form');
    const statusDiv = document.getElementById('settingStatus');
    const formData = new FormData(form);
    formData.append('form_type', formType);

    fetch('/user/profile/sections/setting', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        statusDiv.textContent = data.message;
        statusDiv.style.color = data.success ? 'green' : 'red';
        if (data.success && formType !== 'change-password') form.reset();
    })
    .catch(error => {
        statusDiv.textContent = "Error: " + error.message;
        statusDiv.style.color = 'red';
    });
}

document.querySelector('[data-section="settings"]').addEventListener('click', loadUploadSection);
