# Manual Email Sending Feature

## Overview

The Manual Email Sending feature allows users to send templated emails directly to any email address without going through the company search process. This is useful when you already have the recipient's email address and want to send a personalized email using your configured templates.

## How to Access

### From Navigation
- Log in to your account
- Click on **"Send Email"** in the main navigation bar

### From Dashboard
- Go to your Dashboard
- Click on **"Send Manual Email"** in the Quick Actions section

## How to Use

### Prerequisites
Before using the manual email feature, ensure you have:

1. **Email Templates**: At least one email template configured
   - Go to Settings → Email Templates to create templates
   - Templates can use variables like `{company_name}`, `{hr_name}`, etc.

2. **SMTP Configuration**: At least one verified SMTP configuration
   - Go to Settings → SMTP Configs to set up your email server
   - Test your configuration to ensure it works

### Sending an Email

1. **Select Template and SMTP Config**
   - Choose an email template from the dropdown
   - Select an SMTP configuration to send from

2. **Enter Recipient Information**
   - **HR Email** (required): The recipient's email address
   - **HR Name** (optional): The recipient's name for personalization

3. **Provide Company Information**
   - **Company Name** (required): The company name
   - **Company Domain** (optional): The company's website
   - **Position** (optional): The job position you're applying for

4. **Send the Email**
   - Review the information
   - Click **"Send Email"** to send the templated email

## Template Variables

The following variables are automatically replaced in your email templates:

### Company Information
- `{company_name}` - Company name
- `{company_domain}` - Company website
- `{position}` - Job position

### Recipient Information
- `{hr_name}` - Recipient name
- `{hr_email}` - Recipient email

### Your Information
- `{user_name}` - Your full name
- `{user_email}` - Your email address
- `{user_phone}` - Your phone number

### Other
- `{current_date}` - Current date

## Features

### User-Friendly Interface
- Clean, responsive design
- Form validation with helpful error messages
- Auto-focus on email field for quick entry
- Loading indicator when sending emails

### Quick Actions
- Direct links to create new templates
- Easy access to SMTP configuration management
- Template variables reference for easy lookup

### Success/Error Handling
- Clear success messages when emails are sent
- Detailed error messages if sending fails
- Form preserves data on errors

## Example Workflow

1. **Create a Template** (one-time setup)
   ```
   Subject: Application for {position} Position at {company_name}
   
   Body:
   Dear {hr_name},
   
   I am writing to express my interest in the {position} position at {company_name}.
   
   Best regards,
   {user_name}
   {user_email}
   ```

2. **Configure SMTP** (one-time setup)
   - Add your email provider's SMTP settings
   - Test the configuration

3. **Send Manual Email**
   - Navigate to Send Email page
   - Select your template and SMTP config
   - Enter recipient: john.doe@company.com
   - Enter company: "Tech Corp"
   - Enter position: "Software Engineer"
   - Click Send Email

4. **Result**
   - Email is sent with personalized content
   - Success message confirms delivery

## Benefits

- **Flexibility**: Send emails to any recipient without company search
- **Efficiency**: Reuse templates for consistent messaging
- **Personalization**: Automatic variable replacement
- **Professional**: Use your own SMTP settings for branded emails
- **Quick Access**: Available from multiple locations in the UI

## Technical Implementation

### New Route
- `/send-manual-email` - GET/POST route for the manual email form

### Form Handling
- Uses existing `SendEmailForm` class
- Validates all required fields
- Handles template and SMTP configuration selection

### Email Sending
- Leverages existing `EmailSender` service
- Uses same template rendering system as automated emails
- Provides detailed success/error feedback

### UI Integration
- Added to main navigation for authenticated users
- Integrated into dashboard Quick Actions
- Consistent styling with existing pages

## Security

- Login required for access
- Users can only access their own templates and SMTP configs
- Form validation prevents malicious input
- CSRF protection enabled
