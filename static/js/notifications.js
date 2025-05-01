document.addEventListener('DOMContentLoaded', function() {
    const notificationIcon = document.getElementById('notificationIcon');
    const notificationDropdown = document.getElementById('notificationDropdown');
    
    notificationIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationDropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', function(e) {
        if (!notificationDropdown.contains(e.target)) { 
            notificationDropdown.classList.remove('show');
        }
    });
});
