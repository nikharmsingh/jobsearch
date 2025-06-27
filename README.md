# JobSearch - AI-Powered Job Application Assistant

A modern Flask web application that streamlines the job application process by automatically finding company information, HR contacts, and sending personalized emails.

## Features

### 🎯 Core Functionality

- **Company Domain Discovery**: Automatically find company websites from company names
- **HR Contact Finding**: Locate HR professionals using Apollo.io's extensive database
- **Email Automation**: Send personalized emails with customizable templates
- **User Authentication**: Secure login/registration system
- **SMTP Configuration**: Configure your own email settings

### 🎨 Modern UI

- **Responsive Design**: Bootstrap 5 with custom styling
- **Interactive Dashboard**: Real-time job search tracking
- **Template Management**: Create and manage email templates
- **Progress Tracking**: Monitor application status and history

### 🔧 Technical Features

- **Multiple API Integrations**: Apollo.io, Clearbit, Google Custom Search
- **Secure Data Storage**: Encrypted SMTP passwords
- **Fallback Systems**: Multiple methods for finding contacts
- **Error Handling**: Robust error handling and logging

## Quick Start

### Prerequisites

- Python 3.8+
- Flask and dependencies (see requirements.txt)
- API keys for enhanced functionality (optional)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd jobsearch
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**:

   ```bash
   python init_db.py
   ```

6. **Run the application**:

   ```bash
   python app.py
   ```

7. **Open in browser**:
   ```
   http://localhost:5000
   ```

## Configuration

### Required Environment Variables

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///jobsearch.db

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Optional API Keys (for enhanced functionality)

```bash
# Apollo.io - For HR contact discovery
APOLLO_API_KEY=your-apollo-api-key

# Clearbit - For company information
CLEARBIT_API_KEY=your-clearbit-api-key

# Google Custom Search - For web search fallback
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
```

## API Integrations

### Apollo.io Integration

The application uses Apollo.io for finding HR professionals and company information:

- **HR Contact Discovery**: Searches for HR managers, recruiters, talent acquisition specialists **based in India only**
- **Company Data**: Finds company domains and organization details
- **High-Quality Data**: Verified emails and professional profiles
- **Location Filtering**: All HR searches are automatically filtered to find India-based professionals

See [APOLLO_INTEGRATION.md](APOLLO_INTEGRATION.md) for detailed setup instructions.

### Other Integrations

- **Clearbit**: Company domain and information lookup
- **Google Custom Search**: Web search fallback for company information
- **SMTP**: Email sending with user-configurable settings

## Usage

### 1. Register/Login

- Create an account or login with existing credentials
- Secure authentication with password hashing

### 2. Configure SMTP Settings

- Go to Settings → SMTP Configuration
- Enter your email provider settings
- Test the configuration

### 3. Create Email Templates

- Navigate to Templates
- Create personalized email templates
- Use variables like {company_name}, {contact_name}

### 4. Search for Jobs

- Enter company name in the search form
- System automatically finds:
  - Company domain and information
  - HR contact emails
  - Contact details and LinkedIn profiles

### 5. Send Applications

- Review found contacts
- Select appropriate email template
- Customize message if needed
- Send personalized emails

## Project Structure

```
jobsearch/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── auth/                # Authentication routes
│   ├── main/                # Main application routes
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic services
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── forms.py             # WTForms definitions
├── config.py                # Configuration settings
├── app.py                   # Application entry point
├── init_db.py              # Database initialization
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Database Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/
```

## Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Session Management**: Flask-Login secure sessions
- **Data Encryption**: SMTP passwords encrypted with Fernet
- **Input Validation**: Form validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the documentation
2. Review [APOLLO_INTEGRATION.md](APOLLO_INTEGRATION.md) for API setup
3. Create an issue on GitHub
4. Check logs for error details

## Roadmap

- [ ] Advanced email analytics
- [ ] Integration with job boards
- [ ] AI-powered email personalization
- [ ] Mobile app companion
- [ ] Team collaboration features
