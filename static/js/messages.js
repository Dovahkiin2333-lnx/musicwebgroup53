function loadUploadSection() {
    fetch('/user/profile/sections/messages')
        .then(response => response.text())
        .then(html => {
            document.getElementById('profileContent').innerHTML = html;
            initChatSystem();
        });
}

function initChatSystem() {
    const friendsList = document.querySelector('.friends-list');
    const messagesDisplay = document.querySelector('.messages-display');
    const messageInput = document.querySelector('.message-input');
    const sendButton = document.querySelector('.send-button');
    const noChatSelected = document.querySelector('.no-chat-selected');
    
    let currentFriendId = null;
    let currentFriendName = null;
    let socket = null;
    
    function initSocket() {
        socket = io();
        
        socket.on('new_message', function(data) {
            if (data.sender_id == currentFriendId || data.recipient_id == currentFriendId) {
                const isReceived = data.sender_id == currentFriendId;
                addMessageToDisplay(data, isReceived ? 'received' : 'sent');
                scrollToBottom();
                
                if (!isReceived && document.hidden) {
                    new Notification(`新消息来自 ${currentFriendName}`, {
                        body: data.body
                    });
                }
            }
        });
        

        socket.on('connect', function() {
            console.log('Socket.IO connected');
        });
        

        socket.on('connect_error', function(err) {
            console.error('Socket.IO connection error:', err);
        });
    }
    

    function loadFriends() {
        fetch('/user/profile/friends')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    renderFriendsList(data.friends);
                } else {
                    showError('Failed to load friends: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading friends:', error);
                showError('Failed to load friends. Please try again later.');
            });
    }
    

    function renderFriendsList(friends) {
        if (!friendsList) return;
        
        friendsList.innerHTML = '';
        
        if (friends.length === 0) {
            friendsList.innerHTML = '<div class="no-friends">No friends yet</div>';
            return;
        }
        
        friends.forEach(friend => {
            const friendItem = document.createElement('div');
            friendItem.className = 'friend-item';
            friendItem.dataset.friendId = friend.id;
            

            friendItem.innerHTML = `
                <div class="friend-avatar">${friend.username.charAt(0).toUpperCase()}</div>
                <div class="friend-info">
                    <span class="friend-name">${friend.username}</span>
                    <span class="friend-status">Online</span>
                </div>
            `;
            
            friendItem.addEventListener('click', () => selectFriend(friend.id, friend.username));
            friendsList.appendChild(friendItem);
        });
    }
    

    function selectFriend(friendId, friendName) {
        currentFriendId = friendId;
        currentFriendName = friendName;
        

        document.querySelectorAll('.friend-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.friendId == friendId) {
                item.classList.add('active');
            }
        });
        

        document.querySelector('.chat-title')?.remove();
        const chatTitle = document.createElement('div');
        chatTitle.className = 'chat-title';
        chatTitle.textContent = `Chat with ${friendName}`;
        messagesDisplay?.parentNode.insertBefore(chatTitle, messagesDisplay);
        

        loadMessages(friendId);
        
        if (socket) {
            socket.emit('join_chat', { friend_id: friendId });
        }
    }
    

    function loadMessages(friendId) {
        if (!messagesDisplay || !noChatSelected) return;
        
        fetch(`/user/profile/history?friend_id=${friendId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    renderMessages(data.messages);
                    noChatSelected.style.display = 'none';
                    messagesDisplay.style.display = 'block';
                    scrollToBottom();
                } else {
                    showError('Failed to load messages: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading messages:', error);
                showError('Failed to load messages. Please try again later.');
            });
    }
    
    function renderMessages(messages) {
        if (!messagesDisplay) return;
        
        messagesDisplay.innerHTML = '';
        
        if (messages.length === 0) {
            messagesDisplay.innerHTML = '<div class="no-messages">No messages yet. Start the conversation!</div>';
            return;
        }
        
        messages.forEach(message => {
            const isReceived = message.sender_id == currentFriendId;
            addMessageToDisplay(message, isReceived ? 'received' : 'sent');
        });
    }
    
    function addMessageToDisplay(message, type) {
        if (!messagesDisplay) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        
        const time = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${escapeHtml(message.body)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        messagesDisplay.appendChild(messageElement);
    }
    
    function sendMessage() {
        if (!currentFriendId || !messageInput || !socket) return;
        
        const messageText = messageInput.value.trim();
        if (!messageText) return;
        
        sendButton.disabled = true;
        
        fetch('/user/profile/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipient_id: currentFriendId,
                message: messageText
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                messageInput.value = '';
                if (data.message) {
                    addMessageToDisplay(data.message, 'sent');
                    scrollToBottom();
                }
            } else {
                throw new Error(data.message || 'Failed to send message');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            showError('Failed to send message. Please try again.');
        })
        .finally(() => {
            sendButton.disabled = false;
        });
    }
    

    function scrollToBottom() {
        if (messagesDisplay) {
            messagesDisplay.scrollTop = messagesDisplay.scrollHeight;
        }
    }
    

    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        document.getElementById('profileContent').prepend(errorElement);
        
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }
    
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    if (sendButton && messageInput) {
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    if (Notification.permission !== 'denied') {
        Notification.requestPermission();
    }
    
    initSocket();
    loadFriends();
    

    window.addEventListener('focus', scrollToBottom);
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('[data-section="messages"]')?.addEventListener('click', loadUploadSection);
});
