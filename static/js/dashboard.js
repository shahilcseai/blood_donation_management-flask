// Dashboard interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            this.classList.add('loading');
        });
    });

    // Mark notifications as read
    const notificationLinks = document.querySelectorAll('.notification-item');
    notificationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            this.classList.remove('bg-light');
            this.classList.add('text-muted');
        });
    });
});
