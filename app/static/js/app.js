// JobSearch App JavaScript

// Global app object
const JobSearchApp = {
    // API endpoints
    endpoints: {
        findDomain: '/api/find-company-domain',
        findEmails: '/api/find-hr-emails',
        findEmailsSerp: '/api/find-hr-emails-serp',
        testSMTP: '/api/test-smtp',
        sendTestEmail: '/api/send-test-email',
        sendJobEmail: '/api/send-job-email'
    },

    // Initialize app
    init() {
        this.bindEvents();
        this.initTooltips();
    },

    // Bind event listeners
    bindEvents() {
        // Company domain search
        const domainSearchBtn = document.getElementById('find-domain-btn');
        if (domainSearchBtn) {
            domainSearchBtn.addEventListener('click', this.findCompanyDomain.bind(this));
        }

        // HR email search
        const emailSearchBtn = document.getElementById('find-emails-btn');
        if (emailSearchBtn) {
            emailSearchBtn.addEventListener('click', this.findHREmails.bind(this));
        }

        // SERP API HR email search
        const emailSearchSerpBtn = document.getElementById('find-emails-serp-btn');
        if (emailSearchSerpBtn) {
            emailSearchSerpBtn.addEventListener('click', this.findHREmailsSerp.bind(this));
        }

        // SMTP test
        const smtpTestBtns = document.querySelectorAll('.test-smtp-btn');
        smtpTestBtns.forEach(btn => {
            btn.addEventListener('click', this.testSMTPConfig.bind(this));
        });

        // Send test email
        const testEmailBtns = document.querySelectorAll('.send-test-email-btn');
        testEmailBtns.forEach(btn => {
            btn.addEventListener('click', this.sendTestEmail.bind(this));
        });

        // Send job email
        const sendEmailBtn = document.getElementById('send-email-btn');
        if (sendEmailBtn) {
            sendEmailBtn.addEventListener('click', this.sendJobEmail.bind(this));
        }

        // Template preview
        const templateSelect = document.getElementById('template_id');
        if (templateSelect) {
            templateSelect.addEventListener('change', this.previewTemplate.bind(this));
        }
    },

    // Initialize Bootstrap tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Find company domain
    async findCompanyDomain() {
        const companyName = document.getElementById('company_name').value;
        if (!companyName) {
            this.showAlert('Please enter a company name', 'warning');
            return;
        }

        const btn = document.getElementById('find-domain-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.findDomain, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ company_name: companyName })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('company_domain').value = data.domain;
                this.showAlert(`Found domain: ${data.domain}`, 'success');
            } else {
                this.showAlert(data.message || 'Could not find domain', 'warning');
            }
        } catch (error) {
            this.showAlert('Error finding domain: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Find HR emails
    async findHREmails() {
        const companyName = document.getElementById('company_name').value;
        const companyDomain = document.getElementById('company_domain').value;

        if (!companyName) {
            this.showAlert('Please enter a company name', 'warning');
            return;
        }

        const btn = document.getElementById('find-emails-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.findEmails, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    company_name: companyName,
                    company_domain: companyDomain
                })
            });

            const data = await response.json();

            if (data.success && data.emails.length > 0) {
                this.displayHREmails(data.emails);
                this.showAlert(`Found ${data.count} HR contacts`, 'success');
            } else {
                this.showAlert('No HR contacts found', 'warning');
            }
        } catch (error) {
            this.showAlert('Error finding emails: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Find HR emails using SERP API (India-focused)
    async findHREmailsSerp() {
        const companyName = document.getElementById('company_name').value;
        const companyDomain = document.getElementById('company_domain').value;

        if (!companyName) {
            this.showAlert('Please enter a company name', 'warning');
            return;
        }

        const btn = document.getElementById('find-emails-serp-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching India...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.findEmailsSerp, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    company_name: companyName,
                    company_domain: companyDomain
                })
            });

            const data = await response.json();

            if (data.success && data.emails.length > 0) {
                this.displayHREmailsSerp(data.emails, data.api_info);
                this.showAlert(`SERP API found ${data.count} India-based HR contacts`, 'success');
            } else {
                this.showAlert('SERP API: No India-based HR contacts found', 'warning');
            }
        } catch (error) {
            this.showAlert('SERP API Error: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Display HR emails from SERP API with enhanced information
    displayHREmailsSerp(emails, apiInfo) {
        const container = document.getElementById('hr-emails-container');
        if (!container) return;

        container.innerHTML = '';

        // Add SERP API info header
        const headerCard = document.createElement('div');
        headerCard.className = 'alert alert-info mb-3';
        headerCard.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-info-circle me-2"></i>
                <div>
                    <strong>SERP API Results</strong> - ${apiInfo.focus}<br>
                    <small>Service: ${apiInfo.service} | Search Engine: ${apiInfo.search_engine} | Location: ${apiInfo.geo_location}</small>
                </div>
            </div>
        `;
        container.appendChild(headerCard);

        emails.forEach((email, index) => {
            const emailCard = document.createElement('div');
            emailCard.className = 'card mb-2 border-primary';

            // Enhanced display for SERP API results
            let additionalInfo = '';
            if (email.linkedin_url) {
                additionalInfo += `<br><small><i class="bi bi-linkedin text-primary"></i> <a href="${email.linkedin_url}" target="_blank">LinkedIn Profile</a></small>`;
            }
            if (email.alternative_emails && email.alternative_emails.length > 0) {
                additionalInfo += `<br><small><strong>Alternative emails:</strong> ${email.alternative_emails.slice(0, 2).join(', ')}</small>`;
            }
            if (email.verified_india) {
                additionalInfo += `<br><small><i class="bi bi-geo-alt-fill text-success"></i> Verified India-based</small>`;
            }

            emailCard.innerHTML = `
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h6 class="card-title mb-1">
                                ${email.name}
                                ${email.location === 'India' ? '<span class="badge bg-success ms-2">India</span>' : ''}
                            </h6>
                            <p class="card-text mb-1">
                                <strong>Email:</strong> ${email.email}<br>
                                <strong>Position:</strong> ${email.position}<br>
                                <small class="text-muted">Source: ${email.source} (Confidence: ${email.confidence}%)</small>
                                ${additionalInfo}
                            </p>
                        </div>
                        <div class="col-md-4 text-end">
                            <button class="btn btn-primary btn-sm select-email-btn"
                                    data-name="${email.name}"
                                    data-email="${email.email}">
                                Select
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(emailCard);
        });

        // Add select email event listeners
        this.bindSelectEmailEvents();
    },

    // Display HR emails
    displayHREmails(emails) {
        const container = document.getElementById('hr-emails-container');
        if (!container) return;

        container.innerHTML = '';
        
        emails.forEach((email, index) => {
            const emailCard = document.createElement('div');
            emailCard.className = 'card mb-2';
            emailCard.innerHTML = `
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h6 class="card-title mb-1">${email.name}</h6>
                            <p class="card-text mb-1">
                                <strong>Email:</strong> ${email.email}<br>
                                <strong>Position:</strong> ${email.position}<br>
                                <small class="text-muted">Source: ${email.source} (Confidence: ${email.confidence}%)</small>
                            </p>
                        </div>
                        <div class="col-md-4 text-end">
                            <button class="btn btn-primary btn-sm select-email-btn" 
                                    data-name="${email.name}" 
                                    data-email="${email.email}">
                                Select
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(emailCard);
        });

        // Bind select email events
        this.bindSelectEmailEvents();
    },

    // Bind select email button events
    bindSelectEmailEvents() {
        const container = document.getElementById('hr-emails-container');
        if (!container) return;

        const selectBtns = container.querySelectorAll('.select-email-btn');
        selectBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const name = e.target.dataset.name;
                const email = e.target.dataset.email;

                const hrNameField = document.getElementById('hr_name');
                const hrEmailField = document.getElementById('hr_email');

                if (hrNameField) hrNameField.value = name;
                if (hrEmailField) hrEmailField.value = email;

                this.showAlert('HR contact selected', 'success');
            });
        });
    },

    // Test SMTP configuration
    async testSMTPConfig(event) {
        const btn = event.target;
        const configId = btn.dataset.configId;
        
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testing...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.testSMTP, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ config_id: configId })
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert('SMTP connection successful!', 'success');
            } else {
                this.showAlert('SMTP test failed: ' + data.message, 'danger');
            }
        } catch (error) {
            this.showAlert('Error testing SMTP: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Send test email
    async sendTestEmail(event) {
        const btn = event.target;
        const configId = btn.dataset.configId;
        
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.sendTestEmail, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ config_id: configId })
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert('Test email sent successfully!', 'success');
            } else {
                this.showAlert('Failed to send test email: ' + data.message, 'danger');
            }
        } catch (error) {
            this.showAlert('Error sending test email: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Send job application email
    async sendJobEmail() {
        const form = document.getElementById('send-email-form');
        const formData = new FormData(form);
        
        const data = {
            template_id: formData.get('template_id'),
            smtp_config_id: formData.get('smtp_config_id'),
            hr_email: formData.get('hr_email'),
            hr_name: formData.get('hr_name'),
            company_name: formData.get('company_name'),
            company_domain: formData.get('company_domain'),
            position: formData.get('position')
        };

        const btn = document.getElementById('send-email-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';
        btn.disabled = true;

        try {
            const response = await fetch(this.endpoints.sendJobEmail, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('Email sent successfully!', 'success');
                // Optionally redirect or update UI
            } else {
                this.showAlert('Failed to send email: ' + result.message, 'danger');
            }
        } catch (error) {
            this.showAlert('Error sending email: ' + error.message, 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Preview email template
    previewTemplate() {
        const templateSelect = document.getElementById('template_id');
        const previewContainer = document.getElementById('template-preview');
        
        if (!templateSelect || !previewContainer) return;

        const selectedOption = templateSelect.options[templateSelect.selectedIndex];
        if (selectedOption.value) {
            const subject = selectedOption.dataset.subject || '';
            const body = selectedOption.dataset.body || '';
            
            previewContainer.innerHTML = `
                <div class="email-preview">
                    <div class="email-header">
                        <div class="email-subject">${subject}</div>
                        <div class="email-meta">Template Preview</div>
                    </div>
                    <div class="email-body">${body.replace(/\n/g, '<br>')}</div>
                </div>
            `;
        } else {
            previewContainer.innerHTML = '<p class="text-muted">Select a template to preview</p>';
        }
    },

    // Show alert message
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container') || document.body;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    JobSearchApp.init();
});
