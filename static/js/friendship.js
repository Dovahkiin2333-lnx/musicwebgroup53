document.addEventListener('DOMContentLoaded', function() {
    const friendButton = document.getElementById('friendButton');
    if (friendButton) {
        const socket = io();
        const userId = friendButton.dataset.userId;
        const friendId = friendButton.dataset.friendId;
        const initialStatus = friendButton.dataset.status;
        
        updateButtonState(initialStatus);
        
        friendButton.addEventListener('click', function() {
            if (this.disabled) return;
            
            const currentStatus = this.dataset.status;
            
            if (currentStatus === 'none') {
                socket.emit('friend_request', {
                    sender_id: userId,
                    recipient_id: friendId
                });
                
                this.disabled = true;
                this.textContent = 'Request Sent';
                
            } else if (currentStatus === 'received') {
                socket.emit('accept_friend_request', {
                    sender_id: friendId,  
                    recipient_id: userId
                });
                
                this.disabled = true;
                this.textContent = 'Friends';
            }
        });
        
        socket.on('friend_request_sent', () => {
            friendButton.dataset.status = 'sent';
            friendButton.disabled = false;
        });
        
        socket.on('friend_request_received', (data) => {
            if (parseInt(friendId) === parseInt(data.sender_id)) {
                friendButton.dataset.status = 'received';
                friendButton.textContent = 'Accept Request';
                friendButton.disabled = false;
            }
        });
        
        socket.on('friendship_established', (data) => {
            if (parseInt(friendId) === parseInt(data.friend_id)) {
                friendButton.dataset.status = 'friends';
                friendButton.textContent = 'Friends';
                friendButton.disabled = true;
                
                showNotification(`You are now friends with ${data.friend_name}!`);
            }
        });
    }
    
    function updateButtonState(status) {
        const button = document.getElementById('friendButton');
        if (!button) return;
        
        switch(status) {
            case 'friends':
                button.textContent = 'Friends';
                button.disabled = true;
                break;
            case 'sent':
                button.textContent = 'Request Sent';
                button.disabled = false;
                break;
            case 'received':
                button.textContent = 'Accept Request';
                button.disabled = false;
                break;
            default:
                button.textContent = 'Add Friend';
                button.disabled = false;
        }
        button.dataset.status = status;
    }
    
    function showNotification(message) {
        alert(message); 
    }
});
