function loadUploadSection() {
    const userId = this.dataset.userId

    fetch(`/user/profile/sections/${userId}/posts`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            setupFormSubmission();
        });
}


function deleteSong(songId, buttonElement) {
    if (!confirm('Are you sure you want to delete this song? This action cannot be undone.')) {
        return;
    }
    

    buttonElement.disabled = true;
    buttonElement.textContent = 'Deleting...';
    
    fetch(`/user/profile/delete-song/${songId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            buttonElement.closest('.post-item').remove();
            
            if (document.querySelectorAll('.post-item').length === 0) {
                const container = document.querySelector('.post-container');
                container.innerHTML = '<p class="empty-message">You haven\'t posted any songs yet</p>';
            }
        } else {
            alert(data.message || 'Failed to delete song');
            buttonElement.disabled = false;
            buttonElement.textContent = 'Delete';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the song');
        buttonElement.disabled = false;
        buttonElement.textContent = 'Delete';
    });
}

document.querySelector('[data-section="music"]').addEventListener('click', loadUploadSection);