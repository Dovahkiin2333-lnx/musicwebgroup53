document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.manage-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            
            document.getElementById(this.dataset.tab + '-tab').style.display = 'block';
        });
    });
    function setupOptionSwitcher(sidebarClass) {
        const sidebars = document.querySelectorAll('.' + sidebarClass);
        
        sidebars.forEach(sidebar => {
            const options = sidebar.querySelectorAll('.manage-option');
            const parentContent = sidebar.closest('.tab-content');
            
            options.forEach(option => {
                option.addEventListener('click', function() {
                    options.forEach(opt => opt.classList.remove('active'));
                    this.classList.add('active');
                    
                    const tables = parentContent.querySelectorAll('.manage-table');
                    tables.forEach(table => {
                        table.style.display = 'none';
                    });
                    
                    document.getElementById(this.dataset.option + '-table').style.display = 'block';
                });
            });
        });
    }
    setupOptionSwitcher('manage-sidebar');
    
});