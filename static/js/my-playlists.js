function loadUploadSection() {
    const userId = this.dataset.userId

    fetch(`/user/profile/sections/${userId}/playlists`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            setupFormSubmission();
        });
}



function loadPlaylistSongs(playlistId, rowElement) {
    document.querySelectorAll('.playlist-row').forEach(row => {
        row.classList.remove('active');
    });
    rowElement.classList.add('active');
    

    fetch(`/user/profile/playlist/${playlistId}/songs`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('playlistContent').innerHTML = html;
        });
}


function createPlaylist() {
    const nameInput = document.getElementById('newPlaylistName');
    const playlistName = nameInput.value.trim();
    
    if (!playlistName) {
        alert('Please enter a playlist name');
        return;
    }
    
    fetch('/user/profile/add_playlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: playlistName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadUploadSection();
            nameInput.value = '';
        } else {
            alert(data.message || 'Failed to create playlist');
        }
    });
}

function deletePlaylist(playlistId) {
    if (!confirm('Are you sure you want to delete this playlist?')) return;
    
    fetch(`/user/profile/delete_playlist/${playlistId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadUploadSection();
        } else {
            alert(data.message || 'Failed to delete playlist');
        }
    });
}

function renamePlaylist(playlistId) {
    const newName = document.getElementById('renamePlaylistInput').value.trim();
    
    if (!newName) {
        alert('Please enter a new name');
        return;
    }
    
    fetch(`/user/profile/rename_playlist/${playlistId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_name: newName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadUploadSection();
        } else {
            alert(data.message || 'Failed to rename playlist');
        }
    });
}
function togglePlaylistPrivacy(playlistId, isCurrentlyPublic) {
    const endpoint = isCurrentlyPublic ? '/user/profile/set_private' : '/user/profile/publish_playlist';
    const button = document.getElementById('privacyToggleBtn');
    
    button.disabled = true;
    button.textContent = 'Processing...';
    
    fetch(`${endpoint}/${playlistId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.toggle('public');
            button.classList.toggle('private');
            button.textContent = data.is_public ? 'Set Private' : 'Set Public';
            
            const message = data.is_public ? 
                'Playlist is now public' : 'Playlist is now private';
            showToast(message, 'success');
        } else {
            showToast(data.message || 'Failed to update privacy setting', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    })
    .finally(() => {
        button.disabled = false;
    });
}

function showToast(message, type) {
    alert(message);
}
document.querySelector('[data-section="playlists"]').addEventListener('click', loadUploadSection);