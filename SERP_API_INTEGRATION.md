# SERP API Integration for HR People Search (India-focused)

## Overview

This integration adds SERP API functionality to find HR professionals based in India. The SERP API provides enhanced search capabilities through Google, LinkedIn, and other professional networks with a specific focus on Indian HR professionals.

## Features

### 🎯 India-Focused Search
- Specifically targets HR professionals based in India
- Uses geo-location filtering (gl=in) for India-specific results
- Includes India city keywords in search validation

### 🔍 Multi-Platform Search
- **LinkedIn Profiles**: Direct LinkedIn profile searches for HR professionals
- **Company Websites**: HR team directories and contact pages
- **Job Postings**: HR contacts from job board postings
- **Professional Networks**: RocketReach and other professional directories

### 📊 Enhanced Results
- Real person names and positions
- LinkedIn profile URLs when available
- Alternative email patterns for each person
- Confidence scoring for each contact
- India location verification

## API Configuration

### SERP API Key
The API key is configured in `config.py`:

```python
SERP_API_KEY = os.environ.get('SERP_API_KEY') or 'c1824007c8245f45a13212bad16a4d86581f35eb63b6842cb7eaee14e44bd8d2'
```

### Environment Variable (Recommended)
Set the API key as an environment variable:

```bash
export SERP_API_KEY="your_serp_api_key_here"
```

## Usage

### 1. Web Interface
- Navigate to the company search page
- Enter company name and find domain
- Click **"SERP API (India)"** button
- View India-based HR professionals with enhanced information

### 2. API Endpoint
```bash
POST /api/find-hr-emails-serp
Content-Type: application/json

{
    "company_name": "Google",
    "company_domain": "google.com"
}
```

### 3. Python Service
```python
from app.services import SerpHRFinder

serp_finder = SerpHRFinder()
results = serp_finder.find_hr_professionals("Google", "google.com")
```

## Search Strategies

### 1. LinkedIn HR Profiles
```
"{company_name}" HR Manager India site:linkedin.com
"{company_name}" Human Resources India site:linkedin.com
"{company_name}" Talent Acquisition India site:linkedin.com
"HR Manager at {company_name}" India site:linkedin.com
```

### 2. Company HR Pages
```
site:{company_domain} "HR team" OR "Human Resources" contact India
site:{company_domain} "careers" OR "jobs" contact email India
"{company_name}" HR contact email India
```

### 3. Job Postings
```
"{company_name}" HR contact apply India site:naukri.com
"{company_name}" recruiter contact India site:linkedin.com/jobs
"{company_name}" hiring manager email India
```

### 4. Professional Networks
```
"{company_name}" HR India site:rocketreach.co
"{company_name}" Human Resources India contact
"{company_name}" talent team India email
```

## Result Format

Each HR contact includes:

```json
{
    "name": "Priya Sharma",
    "email": "priya.sharma@company.com",
    "position": "HR Manager",
    "source": "SERP API - LinkedIn Profile",
    "confidence": 85,
    "location": "India",
    "linkedin_url": "https://linkedin.com/in/priya-sharma-hr",
    "alternative_emails": [
        "priyasharma@company.com",
        "p.sharma@company.com"
    ],
    "verified_india": true,
    "serp_metadata": {
        "api_source": "SerpApi",
        "search_engine": "Google",
        "geo_location": "India",
        "language": "English"
    }
}
```

## Integration Points

### 1. Enhanced EmailFinder Service
The existing `EmailFinder` service now includes SERP API as the first search method:

```python
methods = [
    ('SERP API Search', self._try_serp_api_search),     # NEW: India-focused
    ('Job Board Search', self._try_job_board_search),
    ('Company Directory Search', self._try_company_directory_search),
    # ... other methods
]
```

### 2. New API Endpoint
- **Endpoint**: `/api/find-hr-emails-serp`
- **Method**: POST
- **Authentication**: Required (login_required)
- **Focus**: India-based HR professionals

### 3. Enhanced Frontend
- New "SERP API (India)" button in the search interface
- Enhanced result display with India badges and LinkedIn links
- Alternative email suggestions
- SERP API metadata display

## India Location Detection

The system detects India-based professionals using:

```python
india_indicators = [
    'india', 'mumbai', 'delhi', 'bangalore', 'bengaluru', 'hyderabad',
    'chennai', 'pune', 'kolkata', 'ahmedabad', 'gurgaon', 'gurugram',
    'noida', 'kochi', 'chandigarh', 'jaipur', 'indore', 'bhopal'
]
```

## Email Pattern Generation

For each real person found, the system generates likely email patterns:

1. `firstname.lastname@domain.com` (Most common)
2. `firstnamelastname@domain.com`
3. `firstname@domain.com`
4. `f.lastname@domain.com`
5. `firstname_lastname@domain.com`
6. `lastname.firstname@domain.com`

## Rate Limiting & Best Practices

- 1-second delay between search queries
- Maximum 10 results per search
- Deduplication based on email and name
- Confidence scoring for result quality
- Error handling for API failures

## Testing

Run the test script to verify integration:

```bash
python test_serp_integration.py
```

This will test:
- API key configuration
- SERP API connectivity
- HR professional search functionality
- Result formatting and display

## Files Modified/Added

### New Files
- `app/services/serp_hr_finder.py` - Main SERP API service
- `test_serp_integration.py` - Test script
- `SERP_API_INTEGRATION.md` - This documentation

### Modified Files
- `config.py` - Added SERP_API_KEY configuration
- `app/services/__init__.py` - Added SerpHRFinder import
- `app/services/email_finder.py` - Integrated SERP API search
- `app/api/routes.py` - Added SERP API endpoint
- `app/templates/main/search.html` - Added SERP API button
- `app/static/js/app.js` - Added SERP API frontend functionality

## Next Steps

1. **Test the Integration**: Use the test script and web interface
2. **Monitor API Usage**: Track SERP API quota and usage
3. **Enhance Results**: Add more India-specific search patterns
4. **User Feedback**: Collect feedback on result quality
5. **Performance Optimization**: Cache results and optimize queries

## Support

For issues or questions about the SERP API integration:
1. Check the test script output for debugging
2. Verify API key configuration
3. Review SERP API documentation
4. Check rate limiting and quota usage
