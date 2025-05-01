document.getElementById('avatarUpload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const uploadUrl = this.dataset.uploadUrl;
    const csrfToken = this.dataset.csrfToken;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('userAvatar').src = e.target.result;
        
        const formData = new FormData();
        formData.append('avatar', file);
        
        fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
.then(data => {
    if (data.success) {
        document.getElementById('userAvatar').src = data.avatar_url;
        alert('update success!');
    } else {
        alert('fail:' + data.error);
    }
});
    };
    reader.readAsDataURL(file);
});