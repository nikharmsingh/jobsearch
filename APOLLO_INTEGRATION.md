# Apollo.io Integration Guide

This document explains how the JobSearch application integrates with Apollo.io for finding HR contacts and company information.

## Overview

The application has been updated to use Apollo.io instead of Hunter.io for:

- Finding HR professional email addresses
- Discovering company domain information
- Enriching contact data with professional details

## API Key Setup

1. **Get Apollo.io API Key**:

   - Sign up for an Apollo.io account at https://apollo.io
   - Navigate to Settings > API Keys
   - Create a new API key
   - Copy the API key for configuration

2. **Configure Environment Variables**:
   ```bash
   # Add to your .env file
   APOLLO_API_KEY=your-apollo-api-key-here
   ```

## Features

### HR Contact Discovery

The Apollo.io integration searches for HR professionals using these job titles, **specifically targeting India-based professionals only**:

- HR Manager, Human Resources Manager
- HR Director, Human Resources Director
- HR Business Partner, Human Resources Business Partner
- HR Generalist, Human Resources Generalist
- HR Specialist, Human Resources Specialist
- Talent Acquisition Manager, Recruiter, Recruiting Manager
- People Operations, People Ops, Head of People
- Chief People Officer
- HR Coordinator, HR Assistant

**Location Filter**: All searches are automatically filtered to find only HR professionals based in India.

### Company Domain Finding

Apollo.io's organization search helps find company domains by:

- Searching by exact company name
- Finding primary domain from organization data
- Extracting domain from company website URLs

### Data Quality

Apollo.io provides high-quality data with:

- **Verified emails**: Marked with confidence scores
- **Professional details**: Job titles, LinkedIn profiles, organization info
- **Contact enrichment**: Additional context about contacts

## API Usage

### People Search

```python
# Search for HR contacts at a specific company (India-based only)
search_params = {
    "person_titles": ["hr manager", "recruiter", "talent acquisition"],
    "person_locations": ["India"],  # Automatically filters for India-based professionals
    "organization_domains": ["company.com"],
    "per_page": 10
}
```

### Organization Search

```python
# Find company information by name
search_params = {
    "organization_names": ["Company Name"],
    "per_page": 5
}
```

## Rate Limits and Pricing

- Apollo.io API calls consume credits based on your pricing plan
- Free plans have limited API access
- Paid plans offer higher rate limits and more features
- The application respects rate limits and handles errors gracefully

## Error Handling

The integration includes robust error handling:

- Graceful fallback to other search methods if Apollo.io fails
- Proper error logging for debugging
- Timeout handling for API requests
- Invalid response handling

## Data Privacy

- API keys are stored securely in environment variables
- Contact data is processed according to Apollo.io's terms of service
- No sensitive data is logged or stored unnecessarily

## Troubleshooting

### Common Issues

1. **"No API key" errors**:

   - Ensure APOLLO_API_KEY is set in your .env file
   - Verify the API key is valid and active

2. **"No results found" errors**:

   - Try different company name variations
   - Check if the company exists in Apollo.io's database
   - Verify search parameters are correct

3. **Rate limit errors**:
   - Check your Apollo.io plan limits
   - Implement delays between requests if needed
   - Consider upgrading your Apollo.io plan

### Debug Mode

Enable debug logging to see API requests and responses:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Hunter.io

The application has been fully migrated from Hunter.io to Apollo.io:

### Changes Made:

- ✅ Updated configuration to use `APOLLO_API_KEY`
- ✅ Replaced Hunter.io API calls with Apollo.io API calls
- ✅ Updated search parameters and response parsing
- ✅ Enhanced HR title matching for better results
- ✅ Improved error handling and fallback mechanisms

### Benefits of Apollo.io:

- **Better data quality**: More accurate and up-to-date contact information
- **Richer profiles**: LinkedIn URLs, job history, organization details
- **Advanced search**: More sophisticated filtering options
- **Higher success rates**: Better coverage of HR professionals

## Support

For Apollo.io API issues:

- Check Apollo.io documentation: https://docs.apollo.io/
- Contact Apollo.io support for API-specific problems

For application integration issues:

- Check application logs for error details
- Verify environment configuration
- Test API connectivity with simple requests
