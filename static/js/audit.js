document.addEventListener('DOMContentLoaded', function() {
    const options = document.querySelectorAll('.audit-option');
    const tables = document.querySelectorAll('.audit-table');
    
    options.forEach(option => {
        option.addEventListener('click', function() {
            options.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            tables.forEach(table => table.style.display = 'none');
            
            const tableId = this.dataset.type + '-table';
            document.getElementById(tableId).style.display = 'block';
        });
    });
});
