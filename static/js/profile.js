document.addEventListener('DOMContentLoaded', () => {

    const navItems = document.querySelectorAll('.profile-nav-item');
    const contentArea = document.getElementById('profileContent');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            const section = this.dataset.section;
            contentArea.innerHTML = `
                <h3>${this.textContent} Content</h3>
                <p>This would load ${section} content asynchronously</p>
            `;
        });
    });
});