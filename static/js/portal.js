// Portal JavaScript functionality

// Auto-refresh status every 30 seconds
let statusRefreshInterval;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search and filter functionality
    initializeSearch();
    initializeFilter();
    
    // Start auto-refresh if on home page
    if (window.location.pathname === '/') {
        startStatusRefresh();
    }
    
    // Initialize feather icons for dynamically added content
    feather.replace();
});

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        filterApplications(searchTerm, getCurrentCategory());
    });
}

function initializeFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;
    
    categoryFilter.addEventListener('change', function() {
        const selectedCategory = this.value;
        filterApplications(getCurrentSearchTerm(), selectedCategory);
    });
}

function getCurrentSearchTerm() {
    const searchInput = document.getElementById('searchInput');
    return searchInput ? searchInput.value.toLowerCase() : '';
}

function getCurrentCategory() {
    const categoryFilter = document.getElementById('categoryFilter');
    return categoryFilter ? categoryFilter.value : '';
}

function filterApplications(searchTerm, category) {
    const applicationCards = document.querySelectorAll('.application-card');
    
    applicationCards.forEach(card => {
        const name = card.getAttribute('data-name');
        const cardCategory = card.getAttribute('data-category');
        
        const matchesSearch = !searchTerm || name.includes(searchTerm);
        const matchesCategory = !category || cardCategory === category;
        
        if (matchesSearch && matchesCategory) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    const visibleCards = document.querySelectorAll('.application-card[style="display: block"], .application-card:not([style*="display: none"])');
    const noResultsMessage = document.getElementById('noResultsMessage');
    
    if (visibleCards.length === 0 && !noResultsMessage) {
        const grid = document.getElementById('applicationsGrid');
        const message = document.createElement('div');
        message.id = 'noResultsMessage';
        message.className = 'col-12';
        message.innerHTML = `
            <div class="alert alert-warning text-center">
                <i data-feather="search"></i>
                No applications found matching your criteria.
            </div>
        `;
        grid.appendChild(message);
        feather.replace();
    } else if (visibleCards.length > 0 && noResultsMessage) {
        noResultsMessage.remove();
    }
}

function startStatusRefresh() {
    statusRefreshInterval = setInterval(refreshStatus, 30000); // Refresh every 30 seconds
}

function stopStatusRefresh() {
    if (statusRefreshInterval) {
        clearInterval(statusRefreshInterval);
    }
}

function refreshStatus() {
    const statusIndicator = document.getElementById('statusRefresh');
    if (statusIndicator) {
        statusIndicator.style.display = 'block';
    }
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatusBadges(data.applications);
            } else {
                console.error('Failed to refresh status:', data.error);
            }
        })
        .catch(error => {
            console.error('Error refreshing status:', error);
        })
        .finally(() => {
            if (statusIndicator) {
                statusIndicator.style.display = 'none';
            }
        });
}

function updateStatusBadges(applications) {
    applications.forEach(app => {
        const badge = document.querySelector(`[data-app-id="${app.id}"]`);
        if (badge) {
            badge.textContent = app.status;
            badge.className = `badge bg-${app.status === 'running' ? 'success' : 'secondary'} status-badge`;
        }
        
        // Update action buttons
        const card = badge.closest('.card');
        if (card) {
            const footer = card.querySelector('.card-footer');
            if (footer) {
                const buttonContainer = footer.querySelector('.d-flex');
                if (buttonContainer) {
                    const actionButton = buttonContainer.querySelector('a');
                    if (actionButton) {
                        if (app.status === 'running') {
                            actionButton.href = `/stop/${app.id}`;
                            actionButton.className = 'btn btn-danger btn-sm';
                            actionButton.innerHTML = '<i data-feather="stop-circle"></i> Stop';
                        } else {
                            actionButton.href = `/launch/${app.id}`;
                            actionButton.className = 'btn btn-success btn-sm';
                            actionButton.innerHTML = '<i data-feather="play-circle"></i> Launch';
                        }
                    }
                }
            }
        }
    });
    
    // Re-initialize feather icons for updated buttons
    feather.replace();
}

// Show/hide single vs multi-component config sections

document.addEventListener('DOMContentLoaded', function() {
    const singleRadio = document.getElementById('single_app');
    const multiRadio = document.getElementById('multi_app');
    const singleConfig = document.getElementById('single_component_config');
    const multiConfig = document.getElementById('multi_component_config');

    function updateFormVisibility() {
        if (singleRadio && singleRadio.checked) {
            singleConfig.style.display = 'block';
            multiConfig.style.display = 'none';
        } else if (multiRadio && multiRadio.checked) {
            singleConfig.style.display = 'none';
            multiConfig.style.display = 'block';
        }
    }

    if (singleRadio && multiRadio && singleConfig && multiConfig) {
        singleRadio.addEventListener('change', updateFormVisibility);
        multiRadio.addEventListener('change', updateFormVisibility);
        updateFormVisibility(); // Set initial state
    }
});

// Form validation for add application form
document.addEventListener('DOMContentLoaded', function() {
    const addForm = document.querySelector('form[action*="add_application"]');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const id = document.getElementById('id').value;
            const name = document.getElementById('name').value;
            const singleRadio = document.getElementById('single_app');
            const multiRadio = document.getElementById('multi_app');
            if (!/^[a-z0-9-]+$/.test(id)) {
                e.preventDefault();
                alert('Application ID must contain only lowercase letters, numbers, and hyphens.');
                return;
            }
            if (!id || !name) {
                e.preventDefault();
                alert('Please fill in all required fields (ID, Name).');
                return;
            }
            if (singleRadio && singleRadio.checked) {
                const command = document.getElementById('command').value;
                if (!command) {
                    e.preventDefault();
                    alert('Please fill in the Command field for single component applications.');
                    return;
                }
            } else if (multiRadio && multiRadio.checked) {
                // Validate all component fields
                const componentNames = document.getElementsByName('component_name[]');
                const componentCommands = document.getElementsByName('component_command[]');
                const componentWorkingDirs = document.getElementsByName('component_working_dir[]');
                let valid = false;
                for (let i = 0; i < componentNames.length; i++) {
                    if (
                        componentNames[i].value.trim() &&
                        componentCommands[i].value.trim() &&
                        componentWorkingDirs[i].value.trim()
                    ) {
                        valid = true;
                    } else {
                        valid = false;
                        break;
                    }
                }
                if (!valid || componentNames.length === 0) {
                    e.preventDefault();
                    alert('Please fill in all fields (Name, Command, Working Directory) for each component.');
                    return;
                }
            }
        });
    }
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});
