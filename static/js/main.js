// Court Data Fetcher - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation and UI enhancements
    initializeSearchForm();
    initializePDFDownloads();
    initializeTooltips();
});

function initializeSearchForm() {
    const searchForm = document.getElementById('searchForm');
    if (!searchForm) return;

    const submitButton = searchForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;

    searchForm.addEventListener('submit', function(e) {
        // Validate form fields
        const caseType = document.getElementById('case_type').value;
        const caseNumber = document.getElementById('case_number').value.trim();
        const filingYear = document.getElementById('filing_year').value;

        if (!caseType || !caseNumber || !filingYear) {
            e.preventDefault();
            showAlert('Please fill in all required fields.', 'error');
            return;
        }

        // Validate case number format
        if (!/^\d+$/.test(caseNumber)) {
            e.preventDefault();
            showAlert('Case number should contain only numbers.', 'error');
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
        searchForm.classList.add('loading');

        // Show progress message
        setTimeout(() => {
            if (submitButton.disabled) {
                showAlert('Searching court records... This may take a moment.', 'info');
            }
        }, 2000);
    });

    // Reset form state if user navigates back
    window.addEventListener('pageshow', function() {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
        searchForm.classList.remove('loading');
    });
}

function initializePDFDownloads() {
    // Handle PDF download links
    const pdfLinks = document.querySelectorAll('a[href*="download_pdf"]');
    
    pdfLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const linkElement = this;
            const originalText = linkElement.innerHTML;
            
            // Show loading state
            linkElement.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
            linkElement.classList.add('disabled');
            
            // Reset state after timeout (in case of issues)
            setTimeout(() => {
                linkElement.innerHTML = originalText;
                linkElement.classList.remove('disabled');
            }, 10000);
        });
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function showAlert(message, type) {
    // Create and show alert message
    const alertContainer = document.querySelector('.container');
    const alertElement = document.createElement('div');
    
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'info' ? 'alert-info' : 'alert-success';
    
    const iconClass = type === 'error' ? 'fa-exclamation-triangle' : 
                      type === 'info' ? 'fa-info-circle' : 'fa-check-circle';
    
    alertElement.className = `alert ${alertClass} alert-dismissible fade show`;
    alertElement.innerHTML = `
        <i class="fas ${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert after existing alerts or at the top
    const existingAlerts = alertContainer.querySelector('.alert');
    if (existingAlerts) {
        existingAlerts.insertAdjacentElement('afterend', alertElement);
    } else {
        alertContainer.insertAdjacentElement('afterbegin', alertElement);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 5000);
}

// Form validation helpers
function validateCaseNumber(caseNumber) {
    // Remove any non-digit characters
    return caseNumber.replace(/\D/g, '');
}

function formatCaseDisplay(caseType, caseNumber, filingYear) {
    return `${caseType} ${caseNumber}/${filingYear}`;
}

// Utility function to handle network errors
function handleNetworkError(error) {
    console.error('Network error:', error);
    showAlert('Network error occurred. Please check your connection and try again.', 'error');
}

// Auto-format case number input
document.addEventListener('DOMContentLoaded', function() {
    const caseNumberInput = document.getElementById('case_number');
    if (caseNumberInput) {
        caseNumberInput.addEventListener('input', function() {
            this.value = validateCaseNumber(this.value);
        });
    }
});

// Handle back button navigation
window.addEventListener('popstate', function() {
    // Reset any loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.classList.remove('loading');
        const buttons = form.querySelectorAll('button[disabled]');
        buttons.forEach(button => {
            button.disabled = false;
        });
    });
});

// Export functions for use in other scripts if needed
window.CourtDataFetcher = {
    showAlert,
    validateCaseNumber,
    formatCaseDisplay,
    handleNetworkError
};
