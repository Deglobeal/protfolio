// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            const menu = document.getElementById('mobile-menu');
            const icon = this.querySelector('i');
            
            if (menu.classList.contains('hidden')) {
                menu.classList.remove('hidden');
                icon.classList.replace('fa-bars', 'fa-times');
            } else {
                menu.classList.add('hidden');
                icon.classList.replace('fa-times', 'fa-bars');
            }
        });
    }

    // Smooth Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Certificate Filtering
    const categoryButtons = document.querySelectorAll('.category-btn');
    if (categoryButtons.length > 0) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                categoryButtons.forEach(btn => {
                    btn.classList.remove('active', 'bg-blue-600', 'text-white');
                    btn.classList.add('bg-gray-100', 'text-gray-700');
                });
                
                this.classList.add('active', 'bg-blue-600', 'text-white');
                this.classList.remove('bg-gray-100', 'text-gray-700');
                
                const category = this.dataset.category;
                renderCertificates(category);
            });
        });
    }

    // Contact Form Validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Reset errors
            document.querySelectorAll('.text-red-600').forEach(el => {
                el.classList.add('hidden');
            });
            
            // Get form values
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const subject = document.getElementById('subject').value.trim();
            const message = document.getElementById('message').value.trim();
            
            let isValid = true;
            
            // Validate name
            if (!name) {
                document.getElementById('name-error').textContent = 'Name is required';
                document.getElementById('name-error').classList.remove('hidden');
                isValid = false;
            }
            
            // Validate email
            if (!email) {
                document.getElementById('email-error').textContent = 'Email is required';
                document.getElementById('email-error').classList.remove('hidden');
                isValid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                document.getElementById('email-error').textContent = 'Please enter a valid email address';
                document.getElementById('email-error').classList.remove('hidden');
                isValid = false;
            }
            
            // Validate subject
            if (!subject) {
                document.getElementById('subject-error').textContent = 'Subject is required';
                document.getElementById('subject-error').classList.remove('hidden');
                isValid = false;
            }
            
            // Validate message
            if (!message) {
                document.getElementById('message-error').textContent = 'Message is required';
                document.getElementById('message-error').classList.remove('hidden');
                isValid = false;
            } else if (message.length < 10) {
                document.getElementById('message-error').textContent = 'Message must be at least 10 characters long';
                document.getElementById('message-error').classList.remove('hidden');
                isValid = false;
            }
            
            if (isValid) {
                const button = document.querySelector('button[type="submit"]');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Sending Message...';
                button.disabled = true;
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    document.getElementById('success-message').classList.remove('hidden');
                    
                    // Reset form
                    document.getElementById('contact-form').reset();
                    
                    // Hide success message after 5 seconds
                    setTimeout(() => {
                        document.getElementById('success-message').classList.add('hidden');
                    }, 5000);
                }, 2000);
            }
        });
    }

    // Initialize certificates if on certificates page
    if (document.getElementById('certificates-container')) {
        initCertificates();
    }

    // Initialize projects if on projects page
    if (document.getElementById('projects-container')) {
        initProjects();
    }
});

// Certificate functions
function initCertificates() {
    renderCertificates();
    
    // Certificate data
    const certificates = [
        // ... certificate data from certificate.html ...
    ];
    
    window.certificatesData = certificates;
    window.certificatesCategoryIcons = {
        cloud: 'fa-cloud',
        development: 'fa-code',
        devops: 'fa-cogs',
        database: 'fa-database',
        design: 'fa-paint-brush'
    };
    
    renderCertificates();
}

function renderCertificates(category = 'all') {
    const container = document.getElementById('certificates-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    const filteredCerts = category === 'all' 
        ? window.certificatesData 
        : window.certificatesData.filter(cert => cert.category === category);
    
    filteredCerts.forEach(cert => {
        const statusClass = cert.status === 'active' ? 'active-status' : 'completed-status';
        const statusText = cert.status === 'active' ? 'Active' : 'Completed';
        
        const certElement = document.createElement('div');
        certElement.className = 'bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cert-card';
        certElement.innerHTML = `
            <div class="p-6">
                <div class="flex items-start justify-between mb-4">
                    <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                        <i class="fas ${window.certificatesCategoryIcons[cert.category] || 'fa-certificate'} text-2xl text-blue-600"></i>
                    </div>
                    <span class="status-badge ${statusClass}">
                        ${statusText}
                    </span>
                </div>

                <h3 class="text-lg font-bold text-gray-900 mb-2">${cert.title}</h3>
                <p class="text-blue-600 font-medium mb-2">${cert.organization}</p>
                <p class="text-sm text-gray-500 mb-3">${cert.type} • ${cert.date}</p>
                <p class="text-gray-600 text-sm mb-4">${cert.description}</p>

                <div class="mb-4">
                    <div class="flex flex-wrap gap-2">
                        ${cert.skills.map(skill => `
                            <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                                ${skill}
                            </span>
                        `).join('')}
                    </div>
                </div>

                <div class="border-t pt-4">
                    <div class="flex items-center justify-between text-sm text-gray-500 mb-3">
                        <span>ID: ${cert.credentialId}</span>
                        ${cert.expiryDate ? `
                            <span>Expires: ${cert.expiryDate}</span>
                        ` : ''}
                    </div>
                    <a
                        href="${cert.verificationLink}"
                        target="_blank"
                        class="inline-flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                        <i class="fas fa-external-link-alt mr-2"></i>
                        Verify Certificate
                    </a>
                </div>
            </div>
        `;
        
        container.appendChild(certElement);
    });
}

// Project functions
function initProjects() {
    renderProjects();
    
    // Project data
    const projects = [
        // ... project data from project.html ...
    ];
    
    window.projectsData = projects;
    window.projectsCategoryIcons = {
        web: 'fa-globe',
        mobile: 'fa-mobile-alt',
        design: 'fa-paint-brush'
    };
    
    window.projectsStatusColors = {
        Live: 'live-status',
        Completed: 'completed-status'
    };
    
    renderProjects();
    
    // Project filters
    document.getElementById('category-filter').addEventListener('change', function() {
        const category = this.value;
        const tech = document.getElementById('tech-filter').value;
        renderProjects(category, tech);
    });
    
    document.getElementById('tech-filter').addEventListener('change', function() {
        const tech = this.value;
        const category = document.getElementById('category-filter').value;
        renderProjects(category, tech);
    });
    
    // View details buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-details-btn')) {
            const projectId = parseInt(e.target.dataset.id);
            showProjectDetails(projectId);
        }
    });
    
    // Close modal
    document.getElementById('close-modal').addEventListener('click', function() {
        document.getElementById('project-modal').classList.add('hidden');
        document.getElementById('project-modal').classList.remove('flex');
    });
    
    // Close modal when clicking outside
    document.getElementById('project-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.add('hidden');
            this.classList.remove('flex');
        }
    });
}

function renderProjects(category = 'all', tech = 'all') {
    const container = document.getElementById('projects-container');
    const noProjects = document.getElementById('no-projects-message');
    if (!container) return;
    
    container.innerHTML = '';
    
    const filteredProjects = window.projectsData.filter(project => {
        const categoryMatch = category === 'all' || project.category === category;
        const techMatch = tech === 'all' || project.technologies.includes(tech);
        return categoryMatch && techMatch;
    });
    
    if (filteredProjects.length === 0) {
        noProjects.classList.remove('hidden');
    } else {
        noProjects.classList.add('hidden');
        
        filteredProjects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden project-card';
            projectElement.innerHTML = `
                <div class="relative">
                    <div class="w-full h-48 bg-gray-200 flex items-center justify-center">
                        <i class="${window.projectsCategoryIcons[project.category]} text-4xl text-gray-400 category-icon"></i>
                    </div>
                    <div class="absolute top-4 right-4">
                        <span class="status-badge ${window.projectsStatusColors[project.status]}">
                            ${project.status}
                        </span>
                    </div>
                </div>

                <div class="p-6">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-sm text-blue-600 font-medium">
                            ${project.type}
                        </span>
                        <i class="${window.projectsCategoryIcons[project.category]} text-gray-400"></i>
                    </div>

                    <h3 class="text-xl font-bold text-gray-900 mb-3">
                        ${project.title}
                    </h3>
                    
                    <p class="text-gray-600 mb-4 line-clamp-3">
                        ${project.description}
                    </p>

                    <div class="mb-4">
                        <div class="flex flex-wrap gap-2">
                            ${project.technologies.slice(0, 3).map(tech => `
                                <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full tech-badge">
                                    ${tech}
                                </span>
                            `).join('')}
                            ${project.technologies.length > 3 ? `
                                <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                    +${project.technologies.length - 3} more
                                </span>
                            ` : ''}
                        </div>
                    </div>

                    <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                        <button data-id="${project.id}" class="view-details-btn text-blue-600 hover:text-blue-700 font-medium text-sm">
                            View Details
                        </button>
                        
                        <div class="flex space-x-3">
                            ${project.liveDemo ? `
                                <a
                                    href="${project.liveDemo}"
                                    target="_blank"
                                    class="text-gray-600 hover:text-blue-600 transition-colors"
                                    title="Live Demo"
                                >
                                    <i class="fas fa-external-link-alt"></i>
                                </a>
                            ` : ''}
                            ${project.github ? `
                                <a
                                    href="${project.github}"
                                    target="_blank"
                                    class="text-gray-600 hover:text-blue-600 transition-colors"
                                    title="GitHub Repository"
                                >
                                    <i class="fab fa-github"></i>
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(projectElement);
        });
    }
}

function showProjectDetails(projectId) {
    const project = window.projectsData.find(p => p.id === projectId);
    if (!project) return;
    
    const modal = document.getElementById('project-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    
    modalTitle.textContent = project.title;
    
    modalContent.innerHTML = `
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div>
                <div class="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center mb-4">
                    <i class="${window.projectsCategoryIcons[project.category]} text-6xl text-gray-400"></i>
                </div>
                
                <div class="grid grid-cols-2 gap-2">
                    <div class="w-full h-20 bg-gray-100 rounded flex items-center justify-center">
                        <i class="fas fa-image text-gray-400"></i>
                    </div>
                    <div class="w-full h-20 bg-gray-100 rounded flex items-center justify-center">
                        <i class="fas fa-image text-gray-400"></i>
                    </div>
                    <div class="w-full h-20 bg-gray-100 rounded flex items-center justify-center">
                        <i class="fas fa-image text-gray-400"></i>
                    </div>
                    <div class="w-full h-20 bg-gray-100 rounded flex items-center justify-center">
                        <i class="fas fa-image text-gray-400"></i>
                    </div>
                </div>
            </div>

            <div>
                <div class="flex items-center gap-4 mb-4">
                    <span class="status-badge ${window.projectsStatusColors[project.status]}">
                        ${project.status}
                    </span>
                    <span class="text-sm text-gray-600">
                        ${project.type}
                    </span>
                </div>

                <p class="text-gray-600 mb-6">
                    ${project.longDescription}
                </p>

                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div>
                        <h4 class="font-medium text-gray-900 mb-1">Duration</h4>
                        <p class="text-gray-600">${project.duration}</p>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900 mb-1">Client</h4>
                        <p class="text-gray-600">${project.client}</p>
                    </div>
                </div>

                <div class="mb-6">
                    <h4 class="font-medium text-gray-900 mb-3">Technologies Used</h4>
                    <div class="flex flex-wrap gap-2">
                        ${project.technologies.map(tech => `
                            <span class="px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full">
                                ${tech}
                            </span>
                        `).join('')}
                    </div>
                </div>

                <div class="flex gap-4">
                    ${project.liveDemo ? `
                        <a
                            href="${project.liveDemo}"
                            target="_blank"
                            class="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center"
                        >
                            <i class="fas fa-external-link-alt mr-2"></i>
                            Live Demo
                        </a>
                    ` : ''}
                    ${project.github ? `
                        <a
                            href="${project.github}"
                            target="_blank"
                            class="border-2 border-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium hover:border-gray-400 transition-colors flex items-center"
                        >
                            <i class="fab fa-github mr-2"></i>
                            View Code
                        </a>
                    ` : ''}
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
                <h3 class="text-xl font-bold text-gray-900 mb-4">Key Features</h3>
                <ul class="space-y-2">
                    ${project.features.map(feature => `
                        <li class="flex items-start">
                            <i class="fas fa-check text-green-600 mr-3 mt-1"></i>
                            <span class="text-gray-600">${feature}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <div>
                <h3 class="text-xl font-bold text-gray-900 mb-4">Challenges & Solutions</h3>
                <p class="text-gray-600 mb-6">
                    ${project.challenges}
                </p>

                <h3 class="text-xl font-bold text-gray-900 mb-4">Results & Impact</h3>
                <p class="text-gray-600">
                    ${project.results}
                </p>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}